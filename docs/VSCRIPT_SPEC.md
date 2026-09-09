# VScript 技术规范

VScript 与 PyVDisk 是同一个项目。VScript 是运行在 DataDisk/ExecutionService 上的安全工作流语言、CLI、REPL 和盘内脚本运行时。

## 语言与运行时

支持 Lexer、Parser、AST、解释器、变量、表达式、条件、循环、函数、模块、std.fs/vector/log、require、mount、transaction、rollback、WAL、task、await、parallel、cron、触发器、审计和 Host allowlist。

## 安全

禁止 shell、eval、exec、任意 import、反射、进程和网络逃逸。Host 使用 allowlist、realpath/symlink 检查、特殊文件拒绝、大小限制和 atomic write。

## 执行与数据

脚本通过 capability 访问同一 DataDisk 的 FS、Vector、Log、Checkpoint。可由 ExecutionService inline 或 worker-backed 执行；parallel/task/await 当前为确定性顺序语义。单 DataDisk 使用 txid/WAL/participant prepare/commit/abort/recovery，内部 exactly-once 使用 operation_id、结果持久化和 event_id 去重。

## 边界

不实现分布式调度平台，不做多租户和旧格式迁移；外部副作用不在内部 exactly-once 保证内。
