# Agentic API 入口治理

## 推荐入口

新项目统一使用 `DataDisk`、显式 namespace（`disk.fs`、`disk.vector`、`disk.log`、`disk.checkpoints`）和 `ExecutionService`。一个 `.vdisk` 容器承载工作区、语义记忆、事件轨迹、Checkpoint、WAL 与运行状态。

## 使用策略

旧格式、历史别名和旧 API 不再作为架构目标，也不安排迁移或清理工作；它们仅保留为现有代码的实现事实。新代码不要依赖这些入口。底层 `VirtualDisk`、`FS`、`Volume` 和独立 VectorDisk/LogDisk 不是 Agentic 默认入口。

## 执行与安全边界

`ExecutionService` 支持 inline 和可选后台 worker。`DurableQueue` 与 `RunStateStore` 支持持久化状态、租约、heartbeat、幂等、重试和 dead-letter，但仍是单实例基础设施；operation/context 注册表不跨进程恢复。外部副作用必须使用幂等设计。

`ScopedDataDisk` 是 Agent 默认应使用的 capability 视图；普通 `DataDisk` 仅用于受信任的应用管理代码。普通视图不是隔离边界。

## 数据一致性

Vector 支持 generation、index generation、checksum、有限值校验和索引恢复基础。Log 支持 stream sequence、cursor、ack、replay、schema 与 trace metadata。WAL/TransactionParticipant 提供统一 txid 和 intent/prepare/commit/abort 基础，但不等于完整跨 namespace ACID。

## 只读状态命令

`pyvdisk status DATA.vdisk` 只读取 manifest 和 RunState 状态计数，不启动 worker、不恢复任务、不写入数据。

## 当前适用范围

当前适合单机或单实例 Agentic 项目先行使用，并在真实负载下持续增强。不把当前实现当作分布式调度、exactly-once、完整 ACID、完整 HA 或强制终止任意 Python 调用的保证。核心收拢验收覆盖 unified DataDisk E2E、worker/queue、WAL recovery、Volume/Host 和 CLI；当前全量回归为 184 tests passed。