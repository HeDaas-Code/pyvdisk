# VScript 详细使用教程与语言标准

## 1. 简介

VScript 是 PyVDisk 内置的安全批处理与 Agent 工作流语言，文件后缀为 `.vds`。它与 PyVDisk 共用 DataDisk、FS、Vector、Log、Checkpoint、WAL、capability 和 Audit。

## 2. 第一个脚本

```vscript
language "1.0";
let total = 0;
for i in 1..=5 { total += i; }
print(total);
```

执行：

```bash
pyvdisk vscript check job.vds
pyvdisk vscript run job.vds
pyvdisk vscript repl
```

## 3. 语法标准

### 3.1 声明与值

支持 `let`、`const`、数字、字符串、布尔、null、数组、对象、函数和模块。常量不能重新赋值。语句以分号结束，代码块使用花括号。

### 3.2 控制流

支持 `if/else`、`while`、`for ... in`、范围 `1..5` / `1..=5`、`match`、`break`、`continue`、`return` 和 `throw`。

### 3.3 函数与模块

```vscript
fn normalize(value) { return value; }
export fn run(path) { return fs.exists(path); }
```

模块使用 `import` 和 `export`；运行时只加载受允许模块。

## 4. DataDisk 访问

```vscript
require {
  mount data: fs read, write;
  mount memory: vector read, write;
  mount events: log read, append;
}
mount fs data from arg("disk");
```

标准库按 capability 运行：`std.fs` 支持 read/write/append/copy/walk/glob；`std.vector` 支持 collection、upsert、search；`std.log` 支持 append、query、tail。

## 5. 事务与恢复

```vscript
transaction {
  fs.write(data, "/workspace/result", "done");
  log.append(events, "step completed");
} on rollback {
  print("rolled back");
}
```

事务使用 undo、txid、WAL 和 checkpoint。单 DataDisk 内支持 intent/prepare/commit/abort/recovery。

## 6. task、await、parallel

```vscript
parallel {
  task prepare { print("prepare"); }
  task index { print("index"); }
}
```

当前语义是确定性顺序执行，不应理解为自动线程池并发。任务可以被审计、取消或受 deadline 约束。

## 7. Host 与安全

Host 访问必须经过 allowlist capability。系统拒绝 shell、eval、exec、任意 import、反射、进程、网络逃逸、路径穿越、NUL、特殊文件和 symlink escape。

## 8. 解释器设计

<div align="center"><table><tr><th>Source</th><th>Lexer</th><th>Parser</th><th>AST Runtime</th><th>安全执行</th></tr><tr><td>VScript</td><td>Maximal-munch<br>Token + Span</td><td>递归下降<br>Pratt expression</td><td>Tree-walking<br>Env / Closure</td><td>Policy · Budget<br>Capability stdlib · Audit</td></tr></table></div>

Lexer 使用 maximal-munch 并保留 source span；Parser 使用递归下降语句解析和 Pratt 表达式解析；Runtime 通过 Env 链实现词法作用域和闭包。NativeFunction 不允许脚本绕过 capability。

## 9. 错误与资源

词法错误、语法错误、运行时错误、能力错误和资源超限错误都包含可定位信息。Policy/Budget 限制调用深度、循环、读写和 Host 传输。

## 10. CLI 与盘内脚本

```bash
pyvdisk vscript check workflow.vds
pyvdisk vscript run workflow.vds --arg data=agent.vdisk
pyvdisk vscript run-disk tools.vdisk:/.vscript/scripts/job.vds
```

盘内脚本通过只读引导挂载读取，不能借此提升权限。

## 11. 实现边界

VScript 与 PyVDisk 限定单机/单实例；不实现分布式调度平台、多租户或旧格式迁移。内部 exactly-once 不覆盖外部系统；设计目标不自动等于超出当前实现的保证。
