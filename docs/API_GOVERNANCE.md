# PyVDisk 与 VScript API 治理

新项目统一使用 DataDisk、显式 namespace、ScopedDataDisk 和 ExecutionService；VScript 使用同一套模型。

## 推荐入口

```text
disk.fs
disk.vector
disk.log
disk.checkpoints
disk.wal
```

Agent 默认使用 ScopedDataDisk；普通 DataDisk 仅用于受信任管理代码。

## 当前能力

支持 inline/worker、DurableQueue、RunState、lease、heartbeat、retry、idempotency、dead-letter、Audit、WAL、单 DataDisk ACID 生命周期和内部 exactly-once。

## 边界

不实现分布式调度平台；不做多租户和旧格式迁移；外部系统 exactly-once 不属于本项目。`status` 只读输出 DataDisk manifest、namespace 和 RunState 计数。
