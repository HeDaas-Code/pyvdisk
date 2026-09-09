# VScript 1.0 语言设计规范

> 状态：当前实现与演进规范；已实现能力可直接用于项目，未来增强按实际使用反馈推进。设计目标不自动等于已实现保证。  
> 文件后缀：`.vds`  
> 目标运行时：PyVDisk 0.3+  
> 设计原则：确定性、可审计、能力隔离、三类磁盘统一、批处理优先。

## 1. 定位

VScript 是 PyVDisk 的专用批处理语言，用于编排普通文件盘、向量数据盘和日志数据盘。它不是 Python 包装器，也不允许 `eval` 或任意宿主代码执行。

核心能力：

- 统一挂载和操作 `fs/vector/log` 三类 `.vdisk`；
- 变量、表达式、条件、循环、模式匹配；
- 用户函数、模块和标准库；
- 可恢复事务、失败补偿和跨盘协调；
- 结构化并行、task/await、超时和取消；
- cron 定时、日志事件、文件事件触发器；
- CLI、Python API、REPL 和盘内脚本；
- 宿主机目录 allowlist，永不直接执行 shell。

## 2. Hello VDisk

`backup.vds`：

```vscript
language "1.0";

require {
  mount source: fs read;
  mount backup: fs read, write;
}

mount fs source from arg("source");
mount fs backup from arg("backup");

let files = fs.glob(source, "/documents/**/*.pdf");
for path in files {
  let target = "/archive" + path;
  fs.mkdir(backup, path.dirname(target), parents: true);
  fs.copy(source, path, backup, target, overwrite: true);
}

print("copied {files.length} files");
```

执行：

```bash
pyvdisk vscript run backup.vds \
  --arg source=docs.vdisk \
  --arg backup=backup.vdisk \
  --allow-mount docs.vdisk:read \
  --allow-mount backup.vdisk:read,write
```

## 3. 源文件与词法

### 3.1 编码

- UTF-8；
- 分号结束简单语句；块语句不需要分号；
- 标识符允许 Unicode 字母，建议公共 API 使用 ASCII；
- 关键字区分大小写；
- 换行不是语义符号。

### 3.2 注释

```vscript
// 单行注释
/* 可嵌套的
   块注释 */
/// 文档注释，附着到下一个声明
```

### 3.3 字面量

```vscript
null
true false
42 0xff 0b1010
3.14 1.2e6
"UTF-8 字符串"
r"原始字符串"
b"binary\x00"
10KB 64MiB 2GB
250ms 5s 3m 7d
2026-03-20T10:30:00Z
[1, 2, 3]
{"env": "prod", "retry": 3}
`/docs/**/*.pdf`        // path pattern
```

单位采用明确语义：`KB/MB/GB` 为十进制，`KiB/MiB/GiB` 为二进制；时间内部存纳秒。

### 3.4 字符串插值

`"processed {count} records from {disk.label}"`。表达式只求值一次；使用 `{{` 和 `}}` 表示字面花括号。

## 4. 语法（核心 EBNF）

```ebnf
program       = { directive | declaration | statement } EOF ;
directive     = "language" STRING ";" | require_decl | capability_decl ;
declaration   = function_decl | trigger_decl | schedule_decl | import_decl ;
statement     = block | let_stmt | assign_stmt | expr_stmt | if_stmt
              | for_stmt | while_stmt | match_stmt | try_stmt
              | return_stmt | break_stmt | continue_stmt | throw_stmt
              | mount_stmt | transaction_stmt | parallel_stmt
              | defer_stmt | assert_stmt ;
block         = "{" { statement | declaration } "}" ;
let_stmt      = ("let" | "const") IDENT [":" type] "=" expression ";" ;
assign_stmt   = lvalue assign_op expression ";" ;
if_stmt       = "if" expression block { "else" "if" expression block }
                [ "else" block ] ;
for_stmt      = "for" pattern "in" expression block ;
while_stmt    = "while" expression block ;
match_stmt    = "match" expression "{" { pattern ["if" expression] "=>" block } "}" ;
try_stmt      = "try" block { "catch" [pattern] block } ["finally" block] ;
transaction_stmt = "transaction" ["(" tx_options ")"] block
                   ["on" "rollback" block] ["on" "commit" block] ;
parallel_stmt = "parallel" ["(" parallel_options ")"] "{" { task_decl } "}" ;
task_decl     = "task" IDENT block ;
function_decl = ["export"] ["async"] "fn" IDENT "(" [params] ")"
                ["->" type] block ;
import_decl   = "import" module_spec ["as" IDENT] ";" ;
mount_stmt    = "mount" disk_kind IDENT "from" expression ["with" object] ";" ;
expression    = pipeline ;
pipeline      = coalesce { "|>" call_suffix } ;
coalesce      = logical_or { "??" logical_or } ;
logical_or    = logical_and { "or" logical_and } ;
logical_and   = equality { "and" equality } ;
equality      = comparison { ("==" | "!=" | "in" | "not" "in") comparison } ;
comparison    = range { ("<" | "<=" | ">" | ">=") range } ;
range         = additive [ (".." | "..=") additive ] ;
additive      = multiplicative { ("+" | "-") multiplicative } ;
multiplicative = unary { ("*" | "/" | "%") unary } ;
unary         = ("not" | "-" | "+" | "await") unary | postfix ;
postfix       = primary { call | index | member | optional_member } ;
primary       = literal | IDENT | lambda | list | object | "(" expression ")" ;
```

禁止隐式分号插入、动态语法宏和运行时修改 AST。

## 5. 值与类型系统

VScript 采用运行时强类型，函数参数和返回值可选静态注解。编译器在可推断时提前报错。

### 5.1 基础类型

- `Null`、`Bool`、`Int`（有符号 64 位）、`Float`（IEEE 754）；
- `String`、`Bytes`、`Time`、`Duration`、`Size`、`Path`；
- `List<T>`、`Map<K,V>`、`Set<T>`、`Range<T>`；
- `Option<T>`、`Result<T,E>`、`Iterator<T>`、`Task<T>`；
- `FsDisk`、`VectorDisk`、`LogDisk`、`File`、`VectorHit`、`LogEvent`；
- 用户结构体（1.1 计划）；1.0 使用不可变 Map 作为记录。

### 5.2 转换

不允许危险的隐式转换。`Int → Float` 可隐式；其余使用 `int(x)`、`string(x)`、`path(x)`、`json.decode(x)`。

### 5.3 可空值

只有 `Option<T>` 可为 null。可选链 `user?.name`，空值回退 `value ?? default`。

### 5.4 相等与排序

- 容器深度相等；
- 不同数值类型按精确数值比较；
- 磁盘句柄只能比较身份，不可排序；
- Map 的迭代顺序保持插入顺序，序列化按键排序以获得确定结果。

## 6. 控制流

```vscript
let retries = 0;
while retries < 3 {
  try {
    run_job();
    break;
  } catch e: IoError {
    retries += 1;
    time.sleep(100ms * retries);
  }
}

for (index, item) in values.enumerate() {
  if item.disabled { continue; }
  process(index, item);
}

match disk.kind {
  "fs"     => { print("filesystem"); }
  "vector" => { print("vector store"); }
  "log"    => { print("log store"); }
  _        => { throw Error("unsupported"); }
}
```

循环默认受运行时步数限制；可以通过已授权的策略提高限制。

## 7. 函数、闭包和模块

```vscript
/// 批量归档文件
export fn archive(source: FsDisk, target: FsDisk, paths: List<Path>) -> Int {
  let count = 0;
  for path in paths {
    fs.copy(source, path, target, "/archive" + path);
    count += 1;
  }
  return count;
}

let normalize = |text| text.trim().lower();
```

### 7.1 模块来源

```vscript
import "./common.vds" as common;               // 当前脚本目录
import disk("tools", "/scripts/common.vds") as common; // 已挂载盘内
import std.fs as fs;                           // 内置标准库
```

规则：

- 模块首次加载后缓存；循环导入是编译错误；
- 模块顶层只能声明和执行受控初始化；
- 相对宿主导入必须落在 `--allow-module-dir`；
- 盘内模块只允许从带 `script.read` 能力的挂载读取；
- 模块通过 SHA-256 锁文件固定：`vscript.lock`。

## 8. 磁盘挂载与能力

### 8.1 声明

```vscript
require {
  mount docs: fs read, write;
  mount embeddings: vector read, query, mutate;
  mount audit: log append, query;
  host "/srv/import" read;
  host "/srv/export" write;
  network none;
  shell none;
}

mount fs docs from arg("docs");
mount vector embeddings from "vectors.vdisk";
mount log audit from env("AUDIT_DISK");
```

`require` 是脚本请求，不是自行授权。宿主在运行前将请求与 CLI/Policy 授权取交集；缺少能力立即失败。

### 8.2 能力集合

- 通用：`inspect`、`admin`；
- FS：`read`、`write`、`delete`、`metadata`、`fsck`、`grow`；
- Vector：`read`、`query`、`mutate`、`schema`；
- Log：`append`、`query`、`retention`、`compact`、`schema`；
- Script：`script.read`、`script.execute`、`trigger.manage`；
- Host：按规范化后的真实路径和 `read/write` 授权。

符号链接解析后重新做 allowlist 检查，防止路径逃逸。

## 9. 标准库

所有 I/O API 使用命名参数，返回稳定的 VScript 记录，不暴露 Python 对象。

### 9.1 `std.fs`

```text
fs.exists(disk, path) -> Bool
fs.stat(disk, path, follow: true) -> FileStat
fs.list(disk, path, recursive: false) -> List<FileStat>
fs.glob(disk, pattern) -> List<Path>
fs.read(disk, path, offset: 0, length: null) -> Bytes
fs.read_text(disk, path, encoding: "utf-8") -> String
fs.write(disk, path, data, mode: 0o644, overwrite: true)
fs.append(disk, path, data)
fs.mkdir(disk, path, parents: false, mode: 0o755)
fs.copy(src_disk, src, dst_disk, dst, overwrite: false)
fs.move(disk, src, dst, overwrite: false)
fs.remove(disk, path, recursive: false)
fs.chmod / fs.chown / fs.touch / fs.link / fs.symlink
fs.walk(disk, path) -> Iterator<WalkEntry>
fs.df(disk) -> DiskUsage
fs.du(disk, path) -> Size
fs.fsck(disk, repair: false) -> FsckReport
```

### 9.2 `std.vector`

```text
vector.collections(disk)
vector.create_collection(disk, name, dimension, metric: "cosine", ...)
vector.drop_collection(disk, name)
vector.upsert(disk, collection, id, values, metadata: {})
vector.upsert_many(disk, collection, records)
vector.get(disk, collection, id)
vector.delete(disk, collection, id)
vector.count(disk, collection)
vector.search(disk, collection, query, k: 10, where: null)
```

### 9.3 `std.log`

```text
log.streams(disk)
log.create_stream(disk, name, segment_events: 1000,
                  retention: null, max_events: null)
log.drop_stream(disk, name)
log.emit(disk, stream, level, logger, message, fields: {}, tags: {})
log.emit_many(disk, stream, events)
log.query(disk, stream, start: null, end: null, levels: null,
          loggers: null, tags: {}, where: null, limit: null, reverse: false)
log.tail(disk, stream, count: 100)
log.stats(disk, stream)
log.retention(disk, stream)
log.compact(disk, stream)
```

### 9.4 其他模块

- `std.json`、`std.csv`、`std.text`、`std.bytes`；
- `std.path`（纯虚拟路径）和 `std.host`（受控 allowlist）；
- `std.time`、`std.math`、`std.hash`；
- `std.process` **不存在**；
- `std.net` 1.0 不提供。

## 10. 管道

`|>` 将左值作为右侧调用的第一个位置参数：

```vscript
let errors = log.query(audit, "app", levels: ["ERROR"])
  |> list.filter(|e| e.tags.env == "prod")
  |> list.take(100);
```

管道不隐式并行，也不吞掉错误。

## 11. 错误模型

内置层次：

```text
Error
├── CompileError / TypeError
├── CapabilityError
├── ResourceLimitError / CancelledError / TimeoutError
├── IoError / PathError / DiskFullError
├── FsError / VectorError / LogError
├── TransactionError / ConflictError
└── TriggerError / ModuleError
```

`try/catch/finally`、`throw`、`defer`：

```vscript
try {
  fs.write(data, "/result.json", json.encode(result));
} catch e: DiskFullError {
  log.emit(audit, "ops", "ERROR", "job", "disk full", fields: {"error": e.message});
  throw e;
} finally {
  metrics.flush();
}
```

错误包含 `code/message/span/cause/details/stack`。默认只显示 VScript 调用栈，不泄露宿主路径。

## 12. 事务

### 12.1 语义

```vscript
transaction(name: "reindex", isolation: "serializable") {
  fs.write(docs, "/state.json", b"processing");
  vector.upsert_many(embeddings, "docs", vectors);
  log.emit(audit, "jobs", "INFO", "indexer", "committed");
} on rollback {
  print("transaction rolled back");
}
```

1.0 支持单进程内的**可恢复补偿事务**，不是底层块级 ACID。实现方式：

1. 获取所有涉及磁盘的共享全局写锁，按磁盘 UUID 排序避免死锁；
2. 在每块盘创建 `/.vscript/transactions/<txid>/`；
3. 文件覆盖/删除前保存原数据和 inode 元信息；新文件记录删除补偿；
4. 向量变更保存 collection 配置和 records/index 快照；
5. 日志 append 默认标记为 commit-last；rollback 不写审计成功事件；
6. 写 intent → 执行 → 写 prepared → 跨盘依次 commit → 清理 journal；
7. 启动时 recovery 根据状态回滚 intent/prepared，完成 committed 的清理。

### 12.2 限制

- 宿主 import/export、定时器注册、不可逆 admin 操作禁止进入事务；
- 大文件快照受 `max_transaction_bytes` 限制；
- 多盘事务是协调式两阶段提交；进程或机器故障下可恢复，但不承诺分布式共识；
- `transaction(best_effort: true)` 可允许仅有补偿操作的外部副作用，并在结果中报告未补偿项；
- 嵌套 transaction 使用 savepoint，不新建独立提交域。

## 13. 并行与异步

### 13.1 结构化并发

```vscript
parallel(limit: 4, fail: "cancel") {
  task files {
    return build_documents();
  }
  task vectors {
    return rebuild_vectors();
  }
  task logs {
    return log.compact(audit, "app");
  }
}

let result = await files;
```

- task 生命周期不能逃出所属 parallel 块；
- 块退出前隐式 await 所有任务；
- `fail: "cancel" | "collect" | "ignore"`；
- 同一磁盘的写由现有共享 RWLock 序列化，跨盘可真正并行；
- transaction 内禁止 parallel 写同一资源，除非编译器能证明资源不相交；
- `race { ... }` 返回首个成功任务并取消其余（1.1）。

### 13.2 取消

每个循环回边、函数调用和 I/O 前是取消点。取消运行 defer/finally；事务自动回滚。

## 14. 定时和触发器

触发器是声明，不由短命 CLI 进程常驻执行。`pyvdisk vscript daemon` 负责调度；定义存入管理盘 `/.vscript/triggers.json`。

### 14.1 Cron

```vscript
schedule nightly at cron("0 2 * * *", timezone: "Asia/Shanghai") {
  run compact_all();
}
```

### 14.2 日志触发器

```vscript
trigger high_errors on log_event(audit, "app",
  levels: ["ERROR", "CRITICAL"],
  where: {"tags.env": "prod"})
debounce 5s max_parallel 2 {
  notify(event);
}
```

### 14.3 文件触发器

```vscript
trigger inbox on fs_change(docs, "/inbox/**", events: ["create", "modify"])
debounce 1s {
  index_file(event.path);
}
```

当前 FS 无原生事件流，因此 1.0 文件触发器由 daemon 轮询目录快照；日志触发器用 `LogDisk.follow`；计划任务使用单调时钟纠偏。

### 14.4 交付语义

- 默认 at-least-once；
- 每次触发生成 `run_id`，checkpoint 持久化；
- 脚本应使用 `event.id` 或 `run_id` 做幂等键；
- 失败支持指数退避、最大重试和 dead-letter 日志流；
- 触发器捕获脚本版本哈希和 capability policy 哈希。

## 15. 宿主机受控导入导出

```vscript
host.import("/srv/import/data.csv", docs, "/incoming/data.csv");
host.export(docs, "/reports/result.json", "/srv/export/result.json",
            overwrite: false);
```

运行时要求：

- 路径必须是绝对路径；
- `realpath` 后仍位于 allowlist；
- 可分别限制单文件、总字节数和文件数量；
- 默认禁止设备文件、FIFO、socket 和宿主符号链接；
- 临时文件采用安全创建；export 使用 write-temp + atomic rename；
- 永不提供 shell、动态链接库加载和任意 Python 导入。

## 16. 资源限制

Policy 可设置：

```toml
max_steps = 10_000_000
max_wall_time = "10m"
max_memory = "256MiB"
max_tasks = 16
max_open_disks = 8
max_open_files = 128
max_read_bytes = "2GiB"
max_write_bytes = "2GiB"
max_transaction_bytes = "512MiB"
max_call_depth = 256
max_collection_items = 1_000_000
```

运行时按 AST 指令计步；I/O 配额以实际字节记账；超限抛出 `ResourceLimitError`。

## 17. 执行入口

### 17.1 CLI

```text
pyvdisk vscript check SCRIPT
pyvdisk vscript run SCRIPT [--arg K=V] [--json-args FILE]
pyvdisk vscript run-disk DISK:/path/script.vds
pyvdisk vscript repl
pyvdisk vscript fmt SCRIPT
pyvdisk vscript test [PATH]
pyvdisk vscript trigger install/list/remove/enable/disable
pyvdisk vscript daemon --state daemon.vdisk
```

退出码：`0` 成功，`2` 编译错误，`3` 权限错误，`4` 运行错误，`5` 资源限制，`130` 取消。

### 17.2 Python API

```python
from pyvdisk.vscript import Compiler, Runtime, Policy

program = Compiler().compile_file("backup.vds")
policy = Policy.from_toml("vscript-policy.toml")
result = Runtime(policy=policy).run(program, args={"source": "docs.vdisk"})
print(result.value, result.metrics)
```

建议公共对象：`Lexer/Parser/Ast/Compiler/Bytecode/Runtime/Policy/Capability/RunResult/Diagnostic/Scheduler`。

### 17.3 REPL

REPL 默认无能力；用户显式 `:mount docs docs.vdisk read`，宿主再次确认/匹配 policy。支持 `:type`、`:ast`、`:mounts`、`:limits`、`:reset`。

### 17.4 盘内脚本

`DISK:/scripts/job.vds` 先通过已授权的只读 bootstrap 挂载读取，再编译；脚本不能通过自身声明提升该盘权限。执行脚本的 SHA-256 进入审计日志。

## 18. 编译与运行时架构

```text
Source → Lexer → Parser → AST → Name Resolver → Type/Effect Checker
       → Capability Planner → Bytecode Compiler → VM
                                              ↓
                  Capability Broker / Resource Meter
                                              ↓
          FS Adapter | Vector Adapter | Log Adapter | Host Adapter
                                              ↓
         Transaction Coordinator | Scheduler | Audit Sink
```

### 18.1 不使用 Python eval

Parser 推荐手写 Pratt parser + 递归下降语句解析器；VM 执行自定义 bytecode。标准库通过显式注册表绑定，脚本永远拿不到 Python attribute、dunder、模块或对象反射能力。

### 18.2 Effect 检查

函数计算 effect：`pure/read/write/delete/admin/host/trigger`。调用点必须拥有对应能力；pure 函数可安全用于过滤器和并行计算。

### 18.3 确定性

- Map 稳定顺序；
- 时间与随机数只通过注入的 `std.time.now` / `std.random`，测试可替换；
- glob/list 默认按 UTF-8 字节序排序；
- 并行结果通过 task 名读取，不依赖完成顺序；
- 运行记录语言版本、依赖哈希、policy 哈希和参数摘要。

## 19. 审计

每次运行生成结构化审计事件：

```json
{
  "run_id": "...",
  "script_hash": "sha256:...",
  "language": "1.0",
  "principal": "user-or-service",
  "capabilities": ["docs:read", "backup:write"],
  "started_ns": 0,
  "finished_ns": 0,
  "status": "success",
  "reads": 42,
  "writes": 10,
  "bytes_read": 1000,
  "bytes_written": 800
}
```

审计可输出到 stderr、JSON 文件或现有 `LogDiskSink`。敏感参数通过 schema 标记 `secret`，审计只保存哈希。

## 20. 脚本测试

```vscript
test "archive copies files" {
  let source = fixture.fs({"/a.txt": "A"});
  let target = fixture.fs({});
  let count = archive(source, target, ["/a.txt"]);
  assert count == 1;
  assert fs.read_text(target, "/archive/a.txt") == "A";
}
```

测试运行时使用内存/临时 `.vdisk`，虚拟时钟和确定性 task executor。支持 snapshot、expected error、capability denial 测试。

## 21. 完整示例：文件 → 向量 → 审计

```vscript
language "1.0";
import std.fs as fs;
import std.vector as vector;
import std.log as log;

require {
  mount docs: fs read, write;
  mount embeddings: vector read, query, mutate;
  mount audit: log append, query;
}

mount fs docs from arg("docs");
mount vector embeddings from arg("vectors");
mount log audit from arg("logs");

fn chunks(text: String, size: Int) -> List<String> {
  return text.split_chunks(size);
}

fn index_one(path: Path) {
  let text = fs.read_text(docs, path);
  let records = [];
  for (i, chunk) in chunks(text, 1000).enumerate() {
    records.push({
      "id": "{path}:{i}",
      "vector": embedding.from_text(chunk),
      "metadata": {"path": string(path), "chunk": i}
    });
  }
  vector.upsert_many(embeddings, "documents", records);
  return records.length;
}

let paths = fs.glob(docs, `/incoming/**/*.txt`);
let indexed = 0;

transaction(name: "batch-index") {
  parallel(limit: 4, fail: "cancel") {
    for path in paths {
      task "index:{path}" {
        return index_one(path);
      }
    }
  }
  for task in tasks.current() {
    indexed += await task;
  }
  log.emit(audit, "jobs", "INFO", "vscript", "index complete",
           fields: {"files": paths.length, "chunks": indexed},
           tags: {"job": "document-index"});
}

return {"files": paths.length, "chunks": indexed};
```

注：`embedding.from_text` 不是默认内置；必须由宿主注册一个具备 `compute.embedding` effect 的可信扩展。语言不隐含网络模型调用。

## 22. 版本兼容

- 每个脚本必须声明 `language "MAJOR.MINOR"`；
- 同 major 内只增加向后兼容语法/API；
- 废弃至少跨两个 minor；
- bytecode 缓存包含运行时 ABI、源哈希和模块锁哈希；
- 未知 capability、标准库参数或语法在编译阶段失败，不静默忽略。

## 23. 实施路线

### Phase 1：核心 MVP

Lexer、Parser、AST、解释器、诊断；基础类型、let/if/for/fn/try；显式 mount；fs/vector/log 核心绑定；CLI run/check；Policy 和配额。

### Phase 2：工程化

模块、盘内脚本、格式化器、REPL、bytecode VM、审计、脚本测试、宿主 allowlist import/export。

### Phase 3：可靠批处理

单盘 undo journal、recovery、savepoint；结构化并行、取消、超时；跨盘协调事务。

### Phase 4：自动化

触发器存储、daemon、cron、LogDisk follow、FS 轮询事件、重试/dead-letter/checkpoint。

### Phase 5：优化与生态

静态 effect/type 检查增强、LSP、VS Code 扩展、增量编译、可信扩展 SDK、性能分析器。

## 24. 明确不做

VScript 1.0 不提供：任意 shell、任意 Python、网络访问、动态 native library、对象反射、宏系统、隐式全局磁盘、无边界递归、进程创建或真正分布式 ACID。
