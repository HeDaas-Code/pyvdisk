# 变更日志

记录用户可见的变更。版本号与 `pyproject.toml` 的 `version` 一致；更早的历史见 git 提交。
本文件从 issue #1（核心缺口复盘）的修复开始维护，条目按该清单的编号标注。

## [0.4.0] - 2026-09-30

### 新增 — 零依赖与跨平台（issue #2）
- **Windows 兼容层**：新增 `pyvdisk/compat.py`，把全部平台原语收敛到一处 —— 定位读写（`os.pread/pwrite` ↔ `lseek`+`read/write` + 互斥）、文件锁（`fcntl.flock` ↔ `msvcrt.locking`）、目录 `fsync`、`uid/gid`、符号链接探测。此前 `pyvdisk/infrastructure/checkpoint.py` 顶层 `import fcntl`，在 Windows 上连导入都会失败。现在除 `compat.py` 外，包内不再直接触碰这些原语，`tests/test_compat.py` 用一条守卫测试固定该约束。
- **去外部依赖**：`dependencies` 由 `["hnswlib>=0.8.0"]` 改为 `[]`。`VectorDisk` 新增内置 flat 索引后端（`pyvdisk/vector_index.py`），无 hnswlib 时自动回退，查询由 O(log n) 变 O(n) 但结果一致；索引文件带 `PVFLAT01` 魔数标识写入方，**两种后端互相可读**（hnswlib 写的盘无 hnswlib 也能查，反之亦然）。hnswlib / fusepy 降级为可选 extra：`pyvdisk[vector]`、`pyvdisk[fuse]`。
- **单文件快速上手**：新增 `examples/quickstart.py`（仅标准库，Windows / Linux 通用，无外部依赖），自底向上演示块设备、事务与检查点、向量检索、结构化日志、VScript、AgentSandbox。

### 新增 — AgentSandbox（issue #2）
- **`AgentSandbox`**：把 DataDisk 包成可直接交给 Agent 框架的工作区。`create()` / `open()`、`tools(style="openai"|"anthropic"|"mcp")`、`dispatch(name, arguments)`、`call()`（返回结构化 `ToolResult`）、`stats()`。
- **六个内置工具**：`write_file`、`read_file`、`list_files`、`make_directory`、`delete_file`、`run_script`；`read_only=True` 时按 capability 层拒绝写（不只是隐藏工具），`allow_delete=False` 可单独关掉删除。
- **路径空间是镜像不是宿主**：`..` 直接拒绝（不解析，便于审计留痕），`C:\Windows\x` 映射为镜像内 `/C:/Windows/x`；`/.system`、`/.vectors`、`/.logs` 及其清单文件对读写与列举一律不可见，脚本入口（`_SandboxFS`）与 Python 入口共用同一套路径规则。
- **审计**：每次工具调用（含被拒绝的调用）写入哈希链审计流 `agent-audit`，记录工具名、参数、状态、错误类型与能力摘要；`audit()` / `verify_audit()` / `retain_audit()` 可查、可校验、可裁剪。
- **`run_script`**：盘内 VScript 执行，默认不允许宿主读写（`host_read_roots` / `host_write_roots` 显式开启），脚本超时与输出/写入字节数均受限，避免脚本刷爆模型上下文。

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
