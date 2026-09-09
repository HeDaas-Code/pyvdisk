"""pyvdisk —— 纯 Python 实现的虚拟磁盘与文件系统。

无需管理员权限。核心组件：
    - VirtualDisk: 块级镜像 IO
    - FS / mkfs:    文件系统（inode + 位图 + 目录）
    - VFS:          高层路径式 API
    - VFile:        类文件对象
    - fuse_mount:   可选 FUSE 挂载（需 fusepy）

快速开始：
    from pyvdisk import VFS
    VFS.create("disk.vdisk", 16 * 1024 * 1024)
    with VFS("disk.vdisk") as vfs:
        vfs.write_file("/hello.txt", b"hello world")
        print(vfs.read_file("/hello.txt"))
"""

from .disk import VirtualDisk, DEFAULT_BLOCK_SIZE
from .fs import (
    FS,
    mkfs,
    grow,
    Inode,
    SuperBlock,
    Stat,
    FSError,
    T_FILE,
    T_DIR,
    T_SYMLINK,
    MAX_FILE_SIZE,
)
from .volume import (
    Volume,
    VolumeError,
    VolumeMeta,
    DiskMember,
    create_volume,
    open_volume,
    add_mirror,
    remove_mirror,
    resync_mirror,
    MODE_CONCAT,
    MODE_STRIPE,
    MODE_MIRROR,
)
from .vfs import VFS, VFile
from .identity import (
    DiskIdentity,
    IdentityError,
    probe_disk,
    write_identity_to_block0,
    new_disk_uuid,
)
from .driver import (DiskManager, MountedFS, MountedVector, MountedLog,
                     AssembledVolume)
from .vector_disk import VectorDisk, VectorDiskError, SUPPORTED_METRICS
from .log_disk import LogDisk, LogDiskError
from .logging_core import (
    LogEvent, LogSink, MemorySink, StreamSink, LogDiskSink, UnifiedLogger,
    StandardLoggingHandler, get_logger, log_context, bind_context, clear_context,
)
from .rwlock import RWLock
from .infrastructure import (
    DataDisk, DataDiskError, MetadataTransaction,
    DataInfrastructure, Unified, Container, UnifiedError,
    DurableQueue, PersistentQueue, Queue, QueueTask, QueueError, TaskNotFound, InvalidTaskState, LeaseLost,
      CapabilityNamespace, ScopedDataDisk, ScopedFileNamespace, ScopedVectorNamespace,
      ScopedLogNamespace, ScopedCheckpointNamespace, scoped, scoped_data_disk,
)
from .execution import ExecutionService, ExecutionPlaneAdapter
from .contracts import (
    Capability, CapabilityGrant, DurabilityMode, Durability, BlockDevice,
    NamespaceStore, CollectionStore, Event, EventStore, ExecutionContext,
    RunHandle, ExecutionPlane,
)

__version__ = "0.3.0"

__all__ = [
    "VirtualDisk",
    "DEFAULT_BLOCK_SIZE",
    "FS",
    "mkfs",
    "grow",
    "Inode",
    "SuperBlock",
    "Stat",
    "FSError",
    "T_FILE",
    "T_DIR",
    "T_SYMLINK",
    "MAX_FILE_SIZE",
    "Volume",
    "VolumeError",
    "VolumeMeta",
    "DiskMember",
    "create_volume",
    "open_volume",
    "add_mirror",
    "remove_mirror",
    "resync_mirror",
    "MODE_CONCAT",
    "MODE_STRIPE",
    "MODE_MIRROR",
    "DiskIdentity",
    "IdentityError",
    "probe_disk",
    "write_identity_to_block0",
    "new_disk_uuid",
    "DiskManager",
    "MountedFS",
    "MountedVector",
    "MountedLog",
    "AssembledVolume",
    "VectorDisk",
    "VectorDiskError",
    "SUPPORTED_METRICS",
    "LogDisk",
    "LogDiskError",
    "LogEvent",
    "LogSink",
    "MemorySink",
    "StreamSink",
    "LogDiskSink",
    "UnifiedLogger",
    "StandardLoggingHandler",
    "get_logger",
    "log_context",
    "bind_context",
    "clear_context",
    "RWLock",
    "DataDisk",
    "DataDiskError",
    "DurableQueue", "PersistentQueue", "Queue", "QueueTask", "QueueError", "TaskNotFound", "InvalidTaskState", "LeaseLost",
      "CapabilityNamespace", "ScopedDataDisk", "ScopedFileNamespace", "ScopedVectorNamespace",
      "ScopedLogNamespace", "ScopedCheckpointNamespace", "scoped", "scoped_data_disk",
    "Capability",
    "CapabilityGrant",
    "DurabilityMode",
    "Durability",
    "BlockDevice",
    "NamespaceStore",
    "CollectionStore",
    "Event",
    "EventStore",
    "ExecutionContext",
    "RunHandle",
    "ExecutionPlane",
    "ExecutionService",
    "ExecutionPlaneAdapter",
    "VFS",
    "VFile",
    "__version__",
]