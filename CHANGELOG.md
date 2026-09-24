# 变更日志

记录用户可见的变更。版本号与 `pyproject.toml` 的 `version` 一致；更早的历史见 git 提交。
本文件从 issue #1（核心缺口复盘）的修复开始维护，条目按该清单的编号标注。

## [Unreleased]

### 修复 — ACID 与事务
- **A1** DataDisk 事务不再只覆盖 metadata：FS/Vector/Log 副作用走写前撤销日志（`kind=undo`），`abort()` 可回滚。
- **A2** participant 副作用在崩溃后由持久化的写前补偿日志按逆序补偿，并写入 `compensated` 标记；补偿幂等，重复 mount 结果一致。
- **A3（§8.6 一半）** `abort()`（含 `with` 块抛异常触发的隐式 abort）现在会按 enlist 逆序通知 participant `abort(txid, intents)`，并先把 intent 落盘；此前只有 mount 恢复会通知。
- **A5** VFS 后端的 `CheckpointStore` 也走临时文件 + `fsync` + `os.replace`，与 host 后端一致。

### 修复 — 队列与执行
- **B1** 队列操作体持久化，任务可跨进程续跑。
- **B5** `fail()` 走指数退避 + 抖动 + 最大延迟，不再立即回 `queued`。
- **B9** host 侧 Checkpoint/Queue 使用跨进程 `flock` + 原子替换。
- **C3** ExecutionService 对 Python 可调用对象同样启用 capability（ScopedDataDisk），治理承诺不再被绕过。
- **C4** `submit` 遇到 running 状态不再返回永不完成的 handle。

### 修复 — 日志、WAL 与恢复
- **B2** WAL 支持检查点与截断（`wal.ckpt.json` 记录明细），恢复不再每次全量重放。
- **B7** DataDisk 与 VScript 共用同一份 WAL 实现与恢复入口，`vscript run --wal` 是真实消费者。
- **C1** `LogDisk.compact()` 保留 consumers/event_ids，不再丢游标与去重表。
- **C2** `enforce_retention` 同步清理 `event_ids` 并校验消费者游标。

### 修复 — VScript
- **A4** `?.` 具备真正的空安全语义（`null?.a` 返回 `null`），不再被当成 `.`。
- **C8** 每个可撤销的 `fs.*` 变更都在生效**之前**记账，进程内回滚与崩溃恢复共用同一份 undo 解释器；旧内容 ≥64 KiB 落 `/.system/tx`，不再整份驻留内存。
- **C9** `host.*` 有了真实入口：`--host-read-root / --host-write-root` 注入 `Policy`，未授权时报错直接给出打开方式。
- **C8/D 附带**：FUSE 桥的 `readlink` 改回 lstat 语义（此前读任何符号链接都返回 EINVAL）；触发器水位线改用单调 `sequence`（此前用随机 uuid 事件 id 做文本比较，会丢约一半事件）；触发器注册即校验 pattern/stream。

### 新增能力
- **B4** 审计可读：`query(run_id/task_id/status/since/until/limit/newest_first)`、显式 `retain()`、默认开启的哈希链 `verify()` 与 `head()`。
- **D** `cron`、`triggers`、`fuse_mount` 从无测试到 69 例覆盖。
- **E** 打包补全 `pyvdisk.infrastructure` / `pyvdisk.vscript` 子包与 `py.typed`；补 `LICENSE`、`CHANGELOG.md`；CI 覆盖 3.9–3.12 与 Lint。

### 已知未完成（issue #1 剩余）
- **A3** Vector 在 `records_checksum` 不符时直接抛错，Log 只做段校验：文档承诺的“校验并按需重建”尚未实现。
- **B3** 无指标/健康检查模块。
- **B6** 无独立 worker 守护进程、优雅 drain 与运行中中断点。
- **C7** 多处全量重建/整文件重写（向量 HNSW、Log segment、`CheckpointStore.set`、RunState 幂等 key 扫描）。
- 边界：VScript 的 `vector.*` / `log.*` 变更不入 undo 记账；嵌套 `transaction` 的子事务在日志中归属自己的 txid。

## [0.3.0]

`pyproject.toml` 当前声明的版本，也是本文件开始维护时的版本。功能范围见 README 与 `docs/`。
