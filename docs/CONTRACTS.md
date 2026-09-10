# PyVDisk 与 VScript 技术契约

PyVDisk 是一个包含 VScript 脚本运行时的单机 Agentic 数据与执行基础设施项目。DataDisk 是统一容器，VScript 是工作流层。

## Storage Plane
DataDisk 包含 FS、Vector、Log、Checkpoint、Metadata 和 WAL。Vector 提供 generation/checksum/index recovery；Log 提供 sequence/cursor/ack/replay/event_id 去重；Volume 提供 mirror degraded fallback。

## Execution Plane
ExecutionService 支持 inline 与可选 worker。DurableQueue 支持 lease、heartbeat、retry、idempotency、dead-letter。RunStateStore 持久化状态，Audit 关联运行元数据。

## ACID 与 exactly-once
单一 DataDisk 内使用统一 txid 和 begin/intent/prepare/apply/commit/abort/recovery 生命周期。内部操作通过 operation_id、结果持久化、队列去重和 event_id 去重避免重复有效效果。外部系统副作用不在范围内。

## 永久边界
不实现分布式调度平台、不做多租户、不做旧格式迁移。不自动恢复任意 Python 执行栈；VScript parallel/task/await 为确定性顺序语义。
