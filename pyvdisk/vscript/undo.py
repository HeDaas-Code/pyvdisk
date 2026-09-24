"""One undo vocabulary for VScript transactions, in memory and in the WAL.

A transaction has to be undoable twice over: while its process is alive, and after
that process died. Both paths used to carry their own idea of what an undo is, and
until issue #1 C8 only ``fs.write``/``fs.append`` recorded one at all -- a rollback
left ``remove``, ``mkdir``, ``move`` and ``link`` applied, because the closures that
did exist could not be written to the log in the first place.

An undo entry is therefore a plain dict so the log can carry it verbatim, and
:func:`apply_undo` is the single interpreter for the in-process rollback and for
the crash recovery that reads the log back.

Bodies are the one thing an entry cannot always hold cheaply, so an old file body at
or above :data:`SPILL_THRESHOLD` is written to the mounted filesystem (under
``/.system/tx``, which the capability layer keeps out of script reach) and the entry
only names it. Below the threshold the body stays inline: that keeps the common case
free of extra I/O while memory stops growing with the size of the rewritten file.
"""
from __future__ import annotations

import posixpath

#: Bodies this large or larger are kept in the store instead of in memory.
SPILL_THRESHOLD = 64 * 1024
#: Spill area inside the mounted filesystem; scripts cannot reach it (see capabilities).
SPILL_ROOT = "/.system/tx"
#: A single path component is limited to 27 bytes in the disk format.
MAX_NAME_BYTES = 27

#: Every undo verb. ``mount`` is added when an entry is written to the log.
KINDS = frozenset({"write", "remove", "mkdir", "rename", "meta", "truncate", "restore_tree", "symlink"})


def normalize(entry):
    """Accept entries written before this vocabulary existed (``kind``/``old``).

    A log written by an earlier version must stay readable: its ``write``/``append``
    operations carried the previous body as ``old``, which is exactly what a
    ``write`` entry holds in ``data``.
    """
    if "undo" in entry:
        return entry
    if entry.get("kind") in ("write", "append"):
        return {"undo": "write", "path": entry["path"], "data": entry.get("old")}
    return entry


def spill_path(token, index):
    """Name one spill slot. ``token`` is per transaction, so the name stays short."""
    name = f"{token}-{index:04d}"
    assert len(name.encode("utf-8")) <= MAX_NAME_BYTES, "spill name exceeds the disk name limit"
    return f"{SPILL_ROOT}/{name}"


def _encode(data):
    """Bytes survive a JSON round trip exactly as latin-1 text."""
    return data.decode("latin1")


def store_body(store, token, index, body):
    """Return the body fields of a ``write`` entry, keeping memory bounded.

    ``body`` of ``None`` means the path did not exist, so undoing removes it; an
    empty body means it existed and was empty, so undoing restores an empty file.
    """
    if body is None or len(body) < SPILL_THRESHOLD:
        return {"data": None if body is None else _encode(body)}
    path = spill_path(token, index)
    try:
        parent = posixpath.dirname(path)
        if not store.exists(parent):
            store.makedirs(parent, 0o700)
        store.write_file(path, body)
    except Exception:
        # A store that cannot hold the spill still has to be able to undo the
        # change: correctness first, bounded memory second.
        return {"data": _encode(body)}
    return {"spill": path}


def load_body(store, entry):
    """Read the body an entry refers to, whether it is inline or spilled."""
    if entry.get("spill") is not None:
        return store.read_file(entry["spill"])
    data = entry.get("data")
    return None if data is None else data.encode("latin1")


def discard_body(store, entry):
    """Drop a spilled body once its entry can no longer be needed."""
    path = entry.get("spill")
    if path is None:
        return
    try:
        if store.exists(path):
            store.rmtree(path) if store.isdir(path) else store.remove(path)
        parent = posixpath.dirname(path)
        if parent and store.exists(parent) and not store.listdir(parent):
            store.rmdir(parent)
    except Exception:
        pass


def spill_conflict(path):
    """True when a snapshot of ``path`` would have to be stored inside ``path``.

    The spill area lives in the same filesystem as the data, so removing an ancestor
    of it would take the undo copy down with the thing it is meant to restore.
    """
    root = path.rstrip("/") or "/"
    return root == "/" or (SPILL_ROOT + "/").startswith(root + "/")


def discard_spill_area(store):
    """Drop the whole spill area. Only safe once no transaction can still need it."""
    try:
        if store.exists(SPILL_ROOT):
            store.rmtree(SPILL_ROOT)
    except Exception:
        pass


def snapshot_tree(store, source, token, index):
    """Copy a tree into the spill area before a recursive remove discards it."""
    dest = spill_path(token, index)
    copy_tree(store, source, dest)
    return dest


def copy_tree(store, source, dest, mode=None):
    """Copy a directory tree (contents, symlink targets and modes) into ``dest``."""
    if not store.exists(dest):
        store.makedirs(dest, mode if mode is not None else 0o755)
    for name in sorted(store.listdir(source)):
        src = posixpath.join(source, name)
        dst = posixpath.join(dest, name)
        info = store.lstat(src)
        if info.is_dir:
            copy_tree(store, src, dst)
        elif info.is_symlink:
            store.symlink(store.readlink(src), dst)
        else:
            store.write_file(dst, store.read_file(src))
            store.chmod(dst, info.mode & 0o7777)
            store.utime(dst, info.atime, info.mtime)
    info = store.lstat(source)
    if info.is_dir:
        store.chmod(dest, info.mode & 0o7777)


def restore_tree(store, spill, target):
    """Put a spilled tree back where it was, then drop the copy."""
    copy_tree(store, spill, target)
    store.rmtree(spill)


def _restore_meta(store, entry):
    path = entry["path"]
    follow = entry.get("follow", True)
    if "mode" in entry:
        store.chmod(path, entry["mode"], follow)
    if "uid" in entry or "gid" in entry:
        store.chown(path, entry.get("uid", -1), entry.get("gid", -1), follow)
    if "atime" in entry or "mtime" in entry:
        store.utime(path, entry.get("atime", -1), entry.get("mtime", -1), follow)


def apply_undo(store, entry):
    """Undo one entry against ``store``.

    Returns True when the entry was applied, False when it is not something this
    interpreter understands. Undoing is best effort in the same sense as the
    compensation it serves: entries are applied in reverse order, and one that finds
    its object already gone did its job.
    """
    kind = entry.get("undo")
    path = entry.get("path")
    if kind not in KINDS:
        return False
    if kind == "write":
        body = load_body(store, entry)
        if body is None:
            if store.exists(path):
                store.remove(path)
        else:
            parent = posixpath.dirname(path)
            if entry.get("parents") and parent and not store.exists(parent):
                store.makedirs(parent, 0o755)
            store.write_file(path, body)
        discard_body(store, entry)
    elif kind == "remove":
        if store.exists(path):
            if entry.get("recursive"):
                store.rmtree(path)
            else:
                store.remove(path)
    elif kind == "mkdir":
        if store.exists(path) and store.isdir(path) and not store.listdir(path):
            store.rmdir(path)
    elif kind == "rename":
        store.rename(path, entry["to"])
    elif kind == "meta":
        _restore_meta(store, entry)
    elif kind == "truncate":
        store.truncate(path, int(entry["size"]))
    elif kind == "restore_tree":
        restore_tree(store, entry["spill"], path)
    elif kind == "symlink":
        store.symlink(entry["link_target"], path)
    return True
