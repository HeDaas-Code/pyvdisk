# PyVDisk 与 VScript 技术契约

PyVDisk 是一个包含 VScript 脚本运行时的单机 Agentic 数据与执行基础设施项目。DataDisk 是统一容器，VScript 是工作流层。

## Storage Plane
DataDisk 包含 FS、Vector、Log、Checkpoint、Metadata 和 WAL。Vector 提供 generation/checksum/index recovery；Log 提供 sequence/cursor/ack/replay/event_id 去重；Volume 提供 mirror degraded fallback。

## Execution Plane
ExecutionService 支持 inline 与可选 worker。DurableQueue 支持 lease、heartbeat、retry、idempotency、dead-letter。RunStateStore 持久化状态，Audit 关联运行元数据。

## ACID 与 exactly-once
单一 DataDisk 内使用统一 txid 和 begin/intent/prepare/apply/commit/abort/recovery 生命周期。内部操作通过 operation_id、结果持久化、队列去重和 event_id 去重避免重复有效效果。外部系统副作用不在范围内。

### 参与者补偿
- **写前补偿日志**：FS / Vector / Log 命名空间的每次变更，在变更生效**之前**先把撤销所需的前像写入 WAL（`kind=undo`）。因此崩溃后仅凭日志即可撤销，不依赖进程内存在的事务对象。
- **恢复期补偿**：mount 时，WAL 中没有 `commit` 记录的事务，其 undo 记录按**逆序**重放，并写入 `kind=compensated` 标记。补偿幂等且可重复——重复 mount 结果一致，第二次 mount 不再重复补偿。
- **已提交事务**：存在 `commit` 记录的事务只做元数据 redo，命名空间副作用被保留，绝不被补偿。
- **第三方 participant**：`enlist` 的 intent 随事务持久化（含载荷）。要在恢复期被补偿，participant 需用 `DataDisk.register_recovery_participant(name, factory)` 注册重建方式，恢复时对其调用 `abort(txid, intents)`；未注册的 participant 只被记录、不被调用，且不会影响恢复本身。
- **可观测**：`DataDisk.recovery_report()` 返回本次 mount 的 `compensated / committed / aborted / participants` 明细。
- **边界**：补偿只覆盖容器内状态；participant 在容器外的副作用（外部 API、支付、邮件）必须由其自身 `abort` 负责。当前 WAL 尚无截断/检查点（见 issue #1 B2），补偿日志会随事务累积。

## 永久边界
不实现分布式调度平台、不做多租户、不做旧格式迁移。不自动恢复任意 Python 执行栈；VScript parallel/task/await 为确定性顺序语义。
