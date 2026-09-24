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
- **进程内 abort 同样通知 participant**：`abort()`（含 `with` 块里抛异常触发的隐式 abort）先持久化 intent，再按 enlist 的**逆序**调用 `abort(txid, intents)`，单个 participant 抛错不影响其余——不等同于"只等下次 mount 恢复"。因此 `abort` 可能被重复调用（崩溃后恢复会再来一次），participant 必须按幂等实现。
- **可观测**：`DataDisk.recovery_report()` 返回本次 mount 的 `compensated / committed / aborted / participants` 明细。
- **边界**：补偿只覆盖容器内状态；participant 在容器外的副作用（外部 API、支付、邮件）必须由其自身 `abort` 负责。

### 日志检查点与恢复入口
- **一份实现**：DataDisk 与 VScript 共用同一份 WAL——同一记录编解码、同一 kind 词表、同一 `recover()`，只是后端不同（镜像内 VFS / 宿主文件）。读取端遇到不认识的 kind 只截断可读前缀，不会假装后面没有 `commit`。
- **结算即截断**：`DataDisk.checkpoint_wal()` 在没有打开事务时结算全部记录——已提交事务的元数据早已发布，未完成事务先被补偿——然后整段丢弃日志；`close()` 与日志超过 `WAL_CHECKPOINT_BYTES`（默认 256 KiB）时自动触发。截断明细写入 `/.system/wal.ckpt.json`（受能力保护）。
- **为什么可以丢弃**：写入永远先于 `commit` 记录落盘，所以 `commit` 一旦持久化，效果就已经在数据里；日志真正要用的是反方向——撤销没提交完的事务。
- **VScript 恢复入口**：`pyvdisk vscript run --wal PATH` 在脚本运行前消费日志、回滚未提交事务，运行结束再结算并截断。挂载没提供时，该事务保持 in-flight（报告为 `deferred`）而不是被标记 aborted——标记 aborted 会静默保留半应用的写入。
- **已知限制**：嵌套 `transaction` 的子事务把操作记录在子事务自己的 txid 下，自己 `commit` 后 WAL 里已是已提交事务。父事务回滚在进程内仍会覆盖它们（undo 会合并给父事务），但若进程在父事务回滚的中途崩溃，恢复只会撤销父事务的条目。

### VScript 事务的撤销记账
- **写前记账**：每条可撤销的变更都在**生效之前**记账（先写 WAL 记录与 in-memory 条目，再改数据），所以"改完但没记上"的窗口不存在。此前只有 `fs.write`/`fs.append` 记账，`remove/mkdir/move/link` 回滚后依然是改过的。
- **一份词表，一个解释器**：`vscript/undo.py` 定义全部 undo 动词——`write`（恢复内容，`body=None` 表示原本不存在）、`remove`、`mkdir`、`rename`、`symlink`、`meta`（mode/uid/gid/atime/mtime）、`truncate`、`restore_tree`（撤销 `remove --recursive`）。进程内回滚与崩溃后的 `recover_wal` 都调用同一个 `apply_undo`，不再各写一套。
- **覆盖范围**：`fs.write / append / copy / mkdir / makedirs / remove（文件、目录、符号链接、递归目录树）/ move / link / symlink / truncate / chmod / chown / utime`。`move` 覆盖了已存在的目标（先记目标旧内容，再记反向 rename）；`truncate` 记旧全文，因为截断丢掉的内容无法用"截回去"找回。
- **旧日志可读**：上一版写下的 `kind=write|append` + `old` 记录会被 `normalize()` 翻译成 `write` 条目，恢复不需要日志迁移。
- **大 body 不留在内存**：旧内容 ≥ `SPILL_THRESHOLD`（64 KiB）时写入挂载内的 `/.system/tx/<token>-<序号>`（`/.system` 对脚本不可达，受能力保护），条目只记路径；阈值以下仍内联，避免常见小文件额外 I/O。`commit` 与 `rollback` 都会回收 spill；spill 槽位名按事务随机短 token 生成，符合单目录项 27 字节上限。整段 spill 区在日志结算后一并清理。
- **边界**：`vector.*` 与 `log.*` 的变更仍然不入 undo 记账（回滚不会撤销 `upsert`/`drop_collection`/`emit`/`compact` 等），这是当前明确的未覆盖面。

### 本地触发器（triggers / cron）
- **水位线是序号，不是事件 id**：`LogEvent.event_id` 是随机 uuid4，拿它做"我处理到哪了"的比较会大约丢掉一半该投递的事件；投递位置取日志单调分配的 `sequence`，没有 sequence 的源才退回 id（此时只有完全相同才视为已投递）。
- **至少一次**：checkpoint 在 handler 成功返回之后才标记，所以 handler 抛错的事件下一轮会被重新投递，而不是被静默跳过；日志触发器因此不能假设 handler 只被调用一次。
- **注册即校验**：`register_file` 必须有 pattern、`register_log` 必须有 stream——否则轮询循环会抛出 `ValueError: Unacceptable pattern`，把守护进程打挂。文件触发器的事件靠内存快照差分（`create`/`modify`/`delete`），进程重启后现有文件会重新按 `create` 上报一次。
- **cron**：五字段（分 时 日 月 周），周字段同时接受 `0` 与 `7` 表示周日；`next_after` 逐分钟前进，超出搜索窗口直接报错而不是返回一个猜测值。

### 宿主文件桥（host.*）
- **默认关闭**：`Policy.host_read_roots / host_write_roots` 默认为空，此时 `host.*` 一律拒绝——空列表表示"没有授权任何根目录"，而不是"路径不合法"，报错会直接给出打开方式。
- **入口**：`pyvdisk vscript run|run-disk|repl --host-read-root DIR --host-write-root DIR`（可重复），或 Python API 里 `Runtime(policy=Policy(host_read_roots=[...], host_write_roots=[...]))`。读写根相互独立：读根只能 `host.read/import_file`，写根才能 `host.write/export_file`。
- **约束**：根目录必须存在；解析后必须落在根内（`realpath` + `commonpath`）；路径中任何一段是符号链接、或目标是特殊文件（fifo/设备）都被拒绝；写入走同目录临时文件 + `fsync` + `os.replace`。

## 永久边界
不实现分布式调度平台、不做多租户、不做旧格式迁移。不自动恢复任意 Python 执行栈；VScript parallel/task/await 为确定性顺序语义。
