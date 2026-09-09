# StoragePlane and ExecutionPlane contracts

本文档描述当前可用于项目集成的边界。具体 Python 定义位于 `pyvdisk/contracts.py`。

## Layer 1 — StoragePlane

`DataDisk` 是推荐容器，提供显式 FS、Vector、Log、Checkpoint、WAL namespace。Vector 提供 generation/checksum 基础；Log 提供 sequence、cursor、ack、replay 和 trace metadata；Volume 提供基础 mirror degraded health 与 fallback。

事务提供统一 txid、intent、prepare、commit、abort 和 WAL recovery 基础。FS、Vector、Log participant 当前是可扩展边界，不宣称完整跨 namespace ACID。

## Layer 2 — ExecutionPlane

`ExecutionContext` 携带 run ID、capabilities、metadata 和 deadline。`ExecutionService` 支持 inline 与可选后台 worker；`DurableQueue` 支持 claim、lease、heartbeat、retry、idempotency 和 dead-letter；`RunStateStore` 持久化运行生命周期；Audit 可关联 run/task/attempt/queue/checkpoint/capability。

## 运行限制

当前是单机/单实例基础设施，不提供分布式 broker、跨进程 callable/context 恢复、exactly-once、任意 Python 调用强制取消或完整跨资源 ACID。取消和 deadline 需要任务协作检查；VScript `parallel/task/await` 当前为确定性顺序执行。

## 项目使用建议

项目可以立即使用当前 P0 能力，边运行边补强。优先使用 `ScopedDataDisk`、可注册操作入口、幂等外部副作用、定期 checkpoint 和审计事件。
