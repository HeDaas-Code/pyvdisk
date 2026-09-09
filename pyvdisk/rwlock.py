"""读写锁（Read-Write Lock）。

提供"多读单写、写互斥"语义：

- 多个读操作可并发持有锁
- 写操作独占：只要有写者持有或正在等待，新读者也要等待（写者优先，防饿死）
- 同线程可重入：持有读锁的线程可再 acquire_read；持有写锁的线程可再
  acquire_write；同线程先读后写会升级（仅当自己是唯一读者时）

主要 API：

    lock = RWLock()
    with lock.read():      # 共享读
        ...
    with lock.write():     # 独占写
        ...

或显式：

    lock.acquire_read(); try: ... finally: lock.release_read()
    lock.acquire_write(); try: ... finally: lock.release_write()

设计为可重入，避免 FS / VFS 内部嵌套调用时死锁。
"""

from __future__ import annotations

import threading
from typing import Optional


class RWLock:
    """可重入读写锁（写者优先）。"""

    def __init__(self):
        self._cond = threading.Condition(threading.RLock())
        self._readers = 0            # 当前活跃读者数
        self._writer: Optional[int] = None  # 当前写者线程 id（None 表示无）
        self._write_recursion = 0    # 写者重入计数
        self._write_waiters = 0      # 等待获取写锁的线程数
        # 每线程读锁重入计数
        self._read_recursion: dict = {}

    # ---- 读锁 ----
    def acquire_read(self) -> "RWLock":
        tid = threading.get_ident()
        with self._cond:
            # 已有读锁：直接重入
            if self._read_recursion.get(tid, 0) > 0:
                self._read_recursion[tid] = self._read_recursion.get(tid, 0) + 1
                return self
            # 已有写锁：同线程，读也算自己，重入
            if self._writer == tid:
                self._read_recursion[tid] = 1
                return self
            # 写者优先：有写者持有或有写者在等，读者等待
            while self._writer is not None or self._write_waiters > 0:
                self._cond.wait()
            self._readers += 1
            self._read_recursion[tid] = 1
            return self

    def release_read(self) -> None:
        tid = threading.get_ident()
        with self._cond:
            cnt = self._read_recursion.get(tid, 0)
            if cnt <= 0:
                raise RuntimeError("release_read 而未持有读锁")
            self._read_recursion[tid] = cnt - 1
            if cnt - 1 == 0:
                del self._read_recursion[tid]
                # 仅当该线程是真正活跃读者时才递减
                if self._writer != tid:
                    self._readers -= 1
                    if self._readers == 0:
                        self._cond.notify_all()

    # ---- 写锁 ----
    def acquire_write(self) -> "RWLock":
        tid = threading.get_ident()
        with self._cond:
            # 已持有写锁：重入
            if self._writer == tid:
                self._write_recursion += 1
                return self
            # 持有读锁：尝试升级
            if self._read_recursion.get(tid, 0) > 0:
                # 只有当自己是唯一读者时才能升级，否则死锁
                if self._readers != 1:
                    raise RuntimeError(
                        "无法从读锁升级到写锁：存在其他读者"
                    )
                # 释放自己的读锁，转为等待写锁
                del self._read_recursion[tid]
                self._readers -= 1
                if self._readers == 0:
                    self._cond.notify_all()
            self._write_waiters += 1
            while self._writer is not None or self._readers > 0:
                self._cond.wait()
            self._write_waiters -= 1
            self._writer = tid
            self._write_recursion = 1
            return self

    def release_write(self) -> None:
        tid = threading.get_ident()
        with self._cond:
            if self._writer != tid:
                raise RuntimeError("release_write 而未持有写锁")
            self._write_recursion -= 1
            if self._write_recursion == 0:
                self._writer = None
                self._cond.notify_all()

    # ---- 上下文管理器辅助 ----
    def read(self) -> "ReadCtx":
        return ReadCtx(self)

    def write(self) -> "WriteCtx":
        return WriteCtx(self)


class ReadCtx:
    def __init__(self, lock: RWLock):
        self._lock = lock

    def __enter__(self) -> RWLock:
        self._lock.acquire_read()
        return self._lock

    def __exit__(self, *exc):
        self._lock.release_read()


class WriteCtx:
    def __init__(self, lock: RWLock):
        self._lock = lock

    def __enter__(self) -> RWLock:
        self._lock.acquire_write()
        return self._lock

    def __exit__(self, *exc):
        self._lock.release_write()
