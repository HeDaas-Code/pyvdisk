# PyVDisk 与 VScript API 治理

新项目统一使用 DataDisk、显式 namespace、ScopedDataDisk 和 ExecutionService；VScript 使用同一套模型。

## 推荐入口

<div align="center"><table><tr><th>DataDisk API</th><th>用途</th></tr><tr><td><code>disk.fs</code></td><td>workspace 文件</td></tr><tr><td><code>disk.vector</code></td><td>语义记忆</td></tr><tr><td><code>disk.log</code></td><td>事件轨迹</td></tr><tr><td><code>disk.checkpoints</code></td><td>进度与结果</td></tr><tr><td><code>disk.wal</code></td><td>事务恢复</td></tr></table></div>

Agent 默认使用 ScopedDataDisk；普通 DataDisk 仅用于受信任管理代码。

## 当前能力

支持 inline/worker、DurableQueue、RunState、lease、heartbeat、retry、idempotency、dead-letter、Audit、WAL、单 DataDisk ACID 生命周期和内部 exactly-once。

## 边界

不实现分布式调度平台；不做多租户和旧格式迁移；外部系统 exactly-once 不属于本项目。`status` 只读输出 DataDisk manifest、namespace 和 RunState 计数。
