"""Vector index backends: hnswlib when it is installed, flat search when it is not.

``hnswlib`` is an accelerator, not a requirement.  It builds a graph index and
answers approximate queries in logarithmic time; without it the package still
has to answer *correct* queries, so this module implements the same surface
``VectorDisk`` uses::

    Index(space=..., dim=...)  ->  init_index / set_ef / add_items /
                                   save_index / load_index / knn_query

Distances follow hnswlib's conventions exactly, so a collection does not change
meaning when the dependency is installed or removed:

===========  ==========================================
``cosine``   ``1 - cosine similarity``
``l2``       squared euclidean distance
``ip``       ``1 - inner product``
===========  ==========================================

Serialised flat indexes start with :data:`MAGIC`.  An hnswlib-written file has no
such header, so :func:`read_kind` can always say which backend wrote a file: a
collection written with hnswlib and opened without it is rebuilt flat instead of
being misread as garbage.

The flat index is O(n) per query and keeps every vector in memory.  That is the
right trade for the quickstart, small collections and CI; ``pip install
pyvdisk[vector]`` is what you want for large ones.
"""

from __future__ import annotations

import math
import os
import struct
from typing import Any, Iterable, List, Optional, Sequence, Tuple

#: Header written in front of a serialised flat index.
MAGIC = b"PVFLAT01"

#: Backends a collection file can have been written by.
KIND_FLAT = "flat"
KIND_HNSW = "hnsw"

SUPPORTED_SPACES = ("cosine", "l2", "ip")


class FlatIndexError(Exception):
    """Raised when a flat index cannot be built, read or written."""


def read_kind(data: bytes) -> str:
    """Which backend wrote ``data``: ``"flat"`` for our own files, else ``"hnsw"``."""
    return KIND_FLAT if data[:len(MAGIC)] == MAGIC else KIND_HNSW


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return math.fsum(x * y for x, y in zip(a, b))


def _norm(a: Sequence[float]) -> float:
    return math.sqrt(math.fsum(x * x for x in a))


def _unit(vector: Sequence[float]) -> List[float]:
    length = _norm(vector)
    if length == 0.0:
        # hnswlib leaves a zero vector alone rather than dividing by zero.
        return list(vector)
    return [x / length for x in vector]


def distance(space: str, a: Sequence[float], b: Sequence[float]) -> float:
    """Distance between two vectors, using hnswlib's convention for ``space``."""
    if space == "cosine":
        return 1.0 - _dot(_unit(a), _unit(b))
    if space == "l2":
        return math.fsum((x - y) ** 2 for x, y in zip(a, b))
    if space == "ip":
        return 1.0 - _dot(a, b)
    raise FlatIndexError(f"未知的距离度量: {space}")


class FlatIndex:
    """Brute-force index with the subset of the hnswlib API that VectorDisk uses."""

    kind = KIND_FLAT

    def __init__(self, space: str = "cosine", dim: int = 0):
        if space not in SUPPORTED_SPACES:
            raise FlatIndexError(f"未知的距离度量: {space}")
        self.space = space
        self.dim = int(dim)
        self.ef = 10
        self.max_elements = 0
        self._labels: List[int] = []
        self._vectors: List[List[float]] = []
        self._position = {}

    # ---- hnswlib-compatible surface -------------------------------------

    def init_index(self, max_elements: int = 0, ef_construction: int = 0, M: int = 0, **_):
        self.max_elements = int(max_elements or 0)

    def set_ef(self, ef: int):
        self.ef = int(ef)

    def add_items(self, vectors: Iterable[Sequence[float]], labels: Iterable[int], **_):
        for vector, label in zip(vectors, labels):
            self.add_item(int(label), vector)

    def add_item(self, label: int, vector: Sequence[float]):
        values = [float(x) for x in vector]
        if self.dim and len(values) != self.dim:
            raise FlatIndexError(f"向量维度不匹配: 期望 {self.dim}，实际 {len(values)}")
        if not self.dim:
            self.dim = len(values)
        if label in self._position:
            self._vectors[self._position[label]] = values
        else:
            self._position[label] = len(self._labels)
            self._labels.append(label)
            self._vectors.append(values)

    def knn_query(self, queries: Iterable[Sequence[float]], k: int = 1, filter=None, **_):
        """Return ``(labels, distances)`` shaped like hnswlib's numpy arrays."""
        out_labels: List[List[int]] = []
        out_distances: List[List[float]] = []
        for query in queries:
            values = [float(x) for x in query]
            scored = []
            for label, vector in zip(self._labels, self._vectors):
                if filter is not None and not filter(label):
                    continue
                scored.append((distance(self.space, values, vector), label))
            # Ties break on the label so repeated queries return a stable order.
            scored.sort(key=lambda pair: (pair[0], pair[1]))
            chosen = scored[:max(0, int(k))]
            out_labels.append([label for _, label in chosen])
            out_distances.append([value for value, _ in chosen])
        return out_labels, out_distances

    def save_index(self, path: str) -> None:
        with open(path, "wb") as stream:
            stream.write(serialize(self))

    def load_index(self, path: str, max_elements: int = 0, **_):
        with open(path, "rb") as stream:
            loaded = deserialize(stream.read())
        self.space = loaded.space
        self.dim = loaded.dim
        self._labels = loaded._labels
        self._vectors = loaded._vectors
        self._position = loaded._position
        self.max_elements = int(max_elements or 0)

    # ---- convenience -----------------------------------------------------

    def __len__(self) -> int:
        return len(self._labels)

    @property
    def labels(self) -> List[int]:
        return list(self._labels)

    def vectors(self) -> List[List[float]]:
        return [list(v) for v in self._vectors]


def serialize(index: FlatIndex) -> bytes:
    """Encode a flat index: header, then labels and float32 vectors."""
    space = index.space.encode("utf-8")
    if len(space) > 255:
        raise FlatIndexError("度量名过长")
    header = struct.pack("<8sBII", MAGIC, len(space), int(index.dim), len(index._labels))
    labels = struct.pack(f"<{len(index._labels)}q", *index._labels) if index._labels else b""
    flat = [value for vector in index._vectors for value in vector]
    vectors = struct.pack(f"<{len(flat)}f", *flat) if flat else b""
    return header + space + labels + vectors


def deserialize(data: bytes) -> FlatIndex:
    """Decode bytes produced by :func:`serialize`."""
    if data[:len(MAGIC)] != MAGIC:
        raise FlatIndexError("不是扁索引文件")
    if len(data) < 17:
        raise FlatIndexError("扁索引头部被截断")
    _, space_length, dim, count = struct.unpack("<8sBII", data[:17])
    space = data[17:17 + space_length].decode("utf-8")
    offset = 17 + space_length
    labels_size = 8 * count
    vectors_size = 4 * count * dim
    if len(data) < offset + labels_size + vectors_size:
        raise FlatIndexError("扁索引数据被截断")
    labels = list(struct.unpack(f"<{count}q", data[offset:offset + labels_size])) if count else []
    offset += labels_size
    values = list(struct.unpack(f"<{count * dim}f", data[offset:offset + vectors_size])) if count and dim else []
    index = FlatIndex(space, dim)
    for position, label in enumerate(labels):
        index._labels.append(label)
        index._position[label] = position
        index._vectors.append(values[position * dim:(position + 1) * dim])
    return index


class _FlatBackend:
    """Module-shaped backend so ``vector_disk`` can treat both alike."""

    kind = KIND_FLAT
    Index = FlatIndex
    MAGIC = MAGIC

    @staticmethod
    def is_available() -> bool:
        return True


#: The object ``vector_disk`` uses when hnswlib is missing.
backend = _FlatBackend()


def serialize_from_backend(index: Any, backend_module: Any) -> bytes:
    """Serialise ``index`` for ``backend_module``, tagging flat files with MAGIC."""
    if getattr(index, "kind", None) == KIND_FLAT:
        return serialize(index)
    handle, host_path = _tempfile()
    try:
        index.save_index(host_path)
        with open(host_path, "rb") as stream:
            return stream.read()
    finally:
        _unlink(host_path)


def _tempfile() -> Tuple[int, str]:
    import tempfile

    return tempfile.mkstemp(suffix=".idx")


def _unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


__all__ = [
    "MAGIC", "KIND_FLAT", "KIND_HNSW", "SUPPORTED_SPACES",
    "FlatIndex", "FlatIndexError", "backend",
    "distance", "read_kind", "serialize", "deserialize", "serialize_from_backend",
]
