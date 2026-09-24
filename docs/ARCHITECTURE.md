# PyVDisk / VScript 详细架构设计

## 1. 总体模型

PyVDisk 与 VScript 是同一个项目的两个协作层：DataDisk 是单机持久化边界，VScript 是安全编排层。项目不实现分布式调度、多租户或旧格式迁移。

<div align="center"><table><tr><th>应用层</th><th>执行层</th><th>数据层</th></tr><tr><td>Agent / Python API / VScript / CLI / REPL</td><td>ExecutionService<br>DurableQueue<br>Worker · Lease · Retry<br>RunState · Audit</td><td>DataDisk<br>FS · Vector · Log<br>Checkpoint · Metadata · WAL</td></tr><tr><th colspan="3">VirtualDisk · FS · Volume · advisory lock · fsync · recovery</th></tr></table></div>

## 2. Storage Plane

DataDisk 将 workspace、语义记忆、事件轨迹、checkpoint、metadata 和 WAL 放在同一个 `.vdisk` 容器中。FS 负责文件；Vector 负责 HNSW 记录及 generation；Log 负责带 sequence 的事件流；Checkpoint 负责结果和进度；WAL 负责事务恢复。

## 3. Execution Plane

ExecutionService 支持 inline 和可选 worker。任务经过 queue claim、lease、heartbeat、operation 执行、RunState 更新和 Audit 记录。取消主要是协作式；deadline、retry 和 idempotency 由任务与执行上下文共同遵守。

## 4. 单机 ACID

事务以 txid 标识，生命周期为 `begin → intent → prepare → apply → commit`，失败则 `abort → recovery`。participant 通过 prepare/commit/abort 参与；WAL 在 remount 时判定 committed、pending 或 aborted。当前保证限定在一个 DataDisk 内。

元数据之外，FS / Vector / Log 命名空间的副作用同样受事务保护：变更生效**之前**先把撤销所需的**前像**写入 WAL；mount 时对没有 `commit` 记录的事务，把这些记录按**逆序**重放（幂等，重复 mount 结果一致），因此不会再出现"元数据回滚了、参与者副作用还在"的部分提交。已提交事务只做 redo，其副作用被保留。第三方 participant 通过 `register_recovery_participant` 注册后，会在恢复期收到 `abort(txid, intents)`；`recovery_report()` 暴露本次恢复的补偿明细。跨出容器的副作用仍由 participant 自行负责。

## 5. 内部 exactly-once

内部操作使用稳定 operation_id 和 idempotency_key；成功结果持久化，重复 queue task 返回既有结果，Log 通过 event_id 去重，Vector 通过 generation/index_generation 检测索引状态。外部 API、支付、邮件和外部数据库不在该保证内。

## 6. VScript 解释器架构

源码先经过 Lexer 生成带位置的 Token，再由递归下降语句解析器和 Pratt 表达式解析器生成 AST。Runtime 使用 tree-walking evaluator，在 Env 链中执行变量和闭包；NativeModule 只暴露 capability-confined 标准库。Policy/Budget 限制调用深度、读写量和资源使用；Audit 记录 source/policy hash、状态和指标。

<div align="center"><table><tr><th>源码</th><th>词法</th><th>语法</th><th>执行</th><th>资源与安全</th></tr><tr><td>VScript</td><td>Lexer<br>Token + Span</td><td>Parser<br>AST</td><td>Runtime<br>Env / Closure</td><td>Policy<br>Budget<br>Capability<br>Audit</td></tr></table></div>

## 7. 设计原则

- 默认安全：无 shell、eval、exec、任意 import、反射和网络逃逸；
- 默认可审计：运行、任务、事务和事件具有可关联 ID；
- 默认确定性：VScript parallel/task/await 当前按确定性顺序执行；
- 显式能力：脚本必须通过 require/mount 获取受限句柄；
- 失败可恢复：WAL、checkpoint、generation、checksum 和 remount recovery；
- 诚实边界：基础设施保证不延伸到外部系统副作用。

## 8. 故障恢复流程

1. 打开并校验 DataDisk；
2. 校验 WAL checksum 和 transaction manifest；
3. 已提交事务（有 `commit` 记录）只做元数据 redo，命名空间副作用保留；
4. 未提交事务：元数据回滚，并按**逆序**重放写前补偿日志撤销参与者副作用，最后写入 `compensated` 标记；
5. 已 abort 事务同样由日志重放补齐——`abort` 记录与补偿完成之间也可能崩溃；
6. 已注册的 participant 通过 `abort(txid, intents)` 收到其持久化 intent；
7. Vector 校验 records/index generation 并按需重建；
8. Log 校验 segment 并恢复 sequence/cursor；
9. RunState 和 Queue 恢复可观察状态，不伪造 Python 执行栈。

## 9. 可观测与运维

`pyvdisk status DATA.vdisk` 是只读状态检查；AuditRecord、RunState、Log sequence、queue attempt 和 checkpoint 用于定位任务。
