"""Structured audit records for VScript executions.

The module deliberately has no storage dependency: applications can provide a
callable or an object with an emit method to Runtime.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Mapping, Optional


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def script_hash(source: Any) -> str:
    """Return a stable SHA-256 digest for script source or an AST fallback."""
    if isinstance(source, str):
        data = source.encode("utf-8")
    elif isinstance(source, bytes):
        data = source
    else:
        data = repr(source).encode("utf-8")
    return _sha256(data)


def policy_hash(policy: Any) -> str:
    """Hash a policy public dataclass fields in canonical JSON form."""
    values = asdict(policy) if hasattr(policy, "__dataclass_fields__") else vars(policy)
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _sha256(encoded)


GENESIS = "0" * 64
AUDIT_MESSAGE = "audit_record"


def row_timestamp(row: Mapping[str, Any]) -> float:
    """When a stored record happened: finished_at, else started_at, else 0."""
    value = row.get("finished_at") or row.get("started_at") or 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def row_hash(row: Mapping[str, Any]) -> str:
    """Canonical digest of one audit row, excluding the row's own hash."""
    body = {k: v for k, v in row.items() if k != "hash"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return _sha256(encoded)


def stamp_row(row: Mapping[str, Any], prev_hash: str = GENESIS) -> dict:
    """Return a chained copy of ``row``."""
    stamped = {k: v for k, v in row.items() if k not in ("prev_hash", "hash")}
    stamped["prev_hash"] = prev_hash
    stamped["hash"] = row_hash(stamped)
    return stamped


def chain_rows(rows: Any, anchor: Optional[str] = None) -> list:
    """Re-stamp a whole sequence, so an unchained log can be adopted."""
    previous = anchor or GENESIS
    chained = []
    for row in rows:
        stamped = stamp_row(row, previous)
        chained.append(stamped)
        previous = stamped["hash"]
    return chained


def chain_head(rows: Any, anchor: Optional[str] = None) -> str:
    """The digest the next emitted row must link back to."""
    for row in reversed(list(rows)):
        if row.get("hash"):
            return str(row["hash"])
    return anchor or GENESIS


def verify_chain(rows: Any, anchor: Optional[str] = None) -> dict:
    """Walk the chain and report the first row that does not link.

    This detects an edit that does not recompute the whole chain. A writer with
    access to the store can always rebuild a consistent chain, which is what the
    returned ``head`` is for: pin it outside the store and a rewrite changes it.
    """
    previous = anchor or GENESIS
    rows = list(rows)
    for index, row in enumerate(rows):
        if not row.get("hash") or not row.get("prev_hash"):
            return {"ok": False, "length": len(rows), "broken_at": index,
                    "reason": "row is not chained", "head": previous}
        if str(row["prev_hash"]) != previous:
            return {"ok": False, "length": len(rows), "broken_at": index,
                    "reason": "prev_hash does not link", "head": previous}
        if row_hash(row) != row["hash"]:
            return {"ok": False, "length": len(rows), "broken_at": index,
                    "reason": "row content changed", "head": previous}
        previous = str(row["hash"])
    return {"ok": True, "length": len(rows), "broken_at": None, "reason": None, "head": previous}


def query_rows(rows: Any, *, run_id: Optional[str] = None, task_id: Optional[str] = None,
               status: Optional[str] = None, since: Optional[float] = None,
               until: Optional[float] = None, limit: Optional[int] = None,
               newest_first: bool = False) -> list:
    """Filter stored rows. Every filter is an exact match; ``None`` means "any".

    ``limit`` keeps the oldest N in order, or the newest N when ``newest_first``.
    """
    if limit is not None and limit < 0:
        raise ValueError("limit must not be negative")
    matched = []
    for row in rows:
        if run_id is not None and row.get("run_id") != run_id:
            continue
        if task_id is not None and row.get("task_id") != task_id:
            continue
        if status is not None and row.get("status") != status:
            continue
        when = row_timestamp(row)
        if since is not None and when < since:
            continue
        if until is not None and when > until:
            continue
        matched.append(row)
    if newest_first:
        matched.reverse()
    return matched[:limit] if limit is not None else matched


def retain_rows(rows: Any, *, max_records: Optional[int] = None,
                max_age_seconds: Optional[float] = None, now: Optional[float] = None):
    """Split rows into ``(kept, dropped)``: by age first, then by count.

    Dropping is explicit -- nothing here prunes on its own -- and the dropped rows
    come back in order so the caller can record the chain head it discarded.
    """
    if max_records is not None and max_records < 0:
        raise ValueError("max_records must not be negative")
    if max_age_seconds is not None and max_age_seconds < 0:
        raise ValueError("max_age_seconds must not be negative")
    rows = list(rows)
    keep = list(range(len(rows)))
    if max_age_seconds is not None:
        cutoff = (time.time() if now is None else now) - max_age_seconds
        keep = [index for index in keep if row_timestamp(rows[index]) >= cutoff]
    if max_records is not None and len(keep) > max_records:
        keep = keep[len(keep) - max_records:]
    kept_indexes = set(keep)
    return [rows[i] for i in keep], [row for i, row in enumerate(rows) if i not in kept_indexes]


@dataclass(frozen=True)
class AuditRecord:
    run_id: str
    script_hash: str
    policy_hash: str
    status: str
    metrics: Mapping[str, Any]
    error: Optional[Mapping[str, str]] = None
    started_at: float = 0.0
    finished_at: float = 0.0
    # Execution-plane correlation fields.  All are optional for old callers.
    task_id: Optional[str] = None
    attempt: Optional[int] = None
    queue_id: Optional[str] = None
    checkpoint_ref: Optional[str] = None
    capability_summary: Optional[Mapping[str, Any]] = None
    parent_run_id: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class CheckpointAuditSink:
    """Small durable sink backed by a CheckpointStore list.

    Rows are hash-chained by default, so an edit that does not recompute the chain
    is detectable. ``adopt()`` re-stamps a log written before chaining existed.
    """
    def __init__(self, store, key="__audit_records__", *, chained=True):
        self.store, self.key, self.chained = store, key, chained
        self.anchor_key = key + ":anchor"

    def _raw(self):
        return list(self.store.get(self.key, []) or [])

    def _anchor(self):
        return self.store.get(self.anchor_key, None) or None

    def _set_anchor(self, value):
        if value:
            self.store.set(self.anchor_key, value)

    def emit(self, record):
        value = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        rows = self._raw()
        if self.chained:
            value = stamp_row(value, chain_head(rows, self._anchor()))
        self.store.set(self.key, rows + [value])

    def records(self):
        return tuple(self._raw())

    def query(self, **filters):
        return tuple(query_rows(self._raw(), **filters))

    def retain(self, *, max_records=None, max_age_seconds=None, now=None):
        """Drop rows by age or count and remember where the chain resumed."""
        rows = self._raw()
        kept, dropped = retain_rows(rows, max_records=max_records, max_age_seconds=max_age_seconds, now=now)
        if dropped:
            if self.chained:
                self._set_anchor(dropped[-1].get("hash") or self._anchor())
            self.store.set(self.key, kept)
        return {"kept": len(kept), "dropped": len(dropped), "anchor": self._anchor()}

    def verify(self):
        return verify_chain(self._raw(), self._anchor())

    def head(self):
        return self.verify()["head"]

    def adopt(self, anchor=None):
        """Re-stamp every stored row so the whole log verifies again."""
        rows = chain_rows(self._raw(), anchor or self._anchor())
        self.store.set(self.key, rows)
        return len(rows)


class DataDiskAuditSink:
    """Persist audit records in a DataDisk structured-log stream.

    Rows are hash-chained by default. The chain lives in the record fields and the
    retention anchor in the disk metadata, so verification resumes correctly after
    rows are dropped. Durability is the backend's; an editor with write access to
    the image can still rebuild a consistent chain, which is what ``head()`` is for.
    """
    ANCHOR_KEY = "__audit_anchor__"
    MESSAGE = AUDIT_MESSAGE

    def __init__(self, disk, stream="audit", *, chained=True):
        self.disk = disk.logs if hasattr(disk, "logs") else disk
        self.stream, self.chained = stream, chained
        self.meta = disk if hasattr(disk, "get_metadata") else None
        if hasattr(self.disk, "list_streams") and not any(
            (item == stream or (isinstance(item, dict) and item.get("name") == stream))
            for item in self.disk.list_streams()
        ):
            self.disk.create_stream(stream)

    def _anchor(self):
        return self.meta.get_metadata(self.ANCHOR_KEY) if self.meta is not None else None

    def _set_anchor(self, value):
        if value and self.meta is not None:
            self.meta.set_metadata(self.ANCHOR_KEY, value)

    def _rows(self):
        return [dict(getattr(event, "fields", {}) or {})
                for event in self.disk.query(self.stream, where={"message": self.MESSAGE})]

    def emit(self, record):
        from ..logging_core import LogEvent
        value = record.to_dict() if hasattr(record, "to_dict") else dict(record)
        if self.chained:
            latest = self.disk.tail(self.stream, 1, where={"message": self.MESSAGE})
            previous = chain_head([getattr(e, "fields", {}) or {} for e in latest], self._anchor())
            value = stamp_row(value, previous)
        self.disk.append(self.stream, LogEvent(time.time_ns(), "INFO", "pyvdisk.audit", self.MESSAGE, fields=value))

    def records(self):
        return tuple(self._rows())

    def query(self, **filters):
        return tuple(query_rows(self._rows(), **filters))

    def retain(self, *, now=None):
        """Hand retention to the log layer, which owns segment lifecycle.

        Segments are append-only, so nothing here rewrites history: the stream's own
        ``retention_seconds`` / ``max_events`` decide what ages out, and this asks the
        log to enforce that policy now rather than on the next append. Create the
        stream yourself to set the policy; the sink reuses an existing one. The chain
        anchor advances to the last row that actually disappeared, so ``verify()``
        resumes past the gap instead of reporting a break.
        """
        before = self._rows()
        self.disk.enforce_retention(self.stream, now_ns=None if now is None else int(now * 1_000_000_000))
        after = self._rows()
        kept = {row.get("hash") for row in after}
        dropped = [row for row in before if row.get("hash") not in kept]
        if dropped and self.chained:
            self._set_anchor(dropped[-1].get("hash") or self._anchor())
        return {"kept": len(after), "dropped": len(dropped), "anchor": self._anchor()}

    def verify(self):
        return verify_chain(self._rows(), self._anchor())

    def head(self):
        return self.verify()["head"]


AuditSink = CheckpointAuditSink
PersistentAuditSink = CheckpointAuditSink


def new_run_id() -> str:
    return str(uuid.uuid4())


def monotonic_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 3)
