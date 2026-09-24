"""VScript transaction logs use the shared WAL implementation.

VScript keeps its log on the host filesystem, so it constructs the same class with
a path instead of a VFS. There is deliberately no second implementation here: two
copies had drifted apart in their record kinds, and the reader that stopped at an
unknown kind silently hid later ``commit`` records.
"""
from __future__ import annotations
from ..infrastructure.wal import WriteAheadLog, WAL, RECORD_KINDS, encode_record, decode_records

__all__ = ["WriteAheadLog", "WAL", "RECORD_KINDS", "encode_record", "decode_records"]
