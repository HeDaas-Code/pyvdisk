"""Safe tree-walking VScript interpreter."""
from __future__ import annotations
import io, operator, time
from .wal import WriteAheadLog
from pathlib import Path
from .parser import parse
from .audit import AuditRecord, new_run_id, policy_hash, script_hash, monotonic_ms

class TransactionContext:
    """In-process undo log; not crash-safe and has no WAL."""
    def __init__(self, runtime):
        self.runtime=runtime; self.undos=[]; self.operations=[]; self.rolling_back=False
        self.txid = runtime.wal.begin() if runtime.wal is not None else None
    def add_operation(self, operation):
        if not self.rolling_back:
            self.operations.append(operation)
            if self.runtime.wal is not None: self.runtime.wal.append(self.txid, operation)
    def add(self, undo):
        if not self.rolling_back: self.undos.append(undo)
    def commit(self):
        if self.runtime.wal is not None: self.runtime.wal.commit(self.txid)
    def rollback(self):
        self.rolling_back=True
        errors=[]
        for undo in reversed(self.undos):
            try: undo()
            except Exception as exc: errors.append(exc)
        if errors: raise RuntimeError(f"事务回滚失败: {errors[0]}")
from dataclasses import dataclass
from . import ast as A
from .errors import RuntimeError, ScriptThrown, ResourceLimitError, CapabilityError
from .policy import Policy, Budget
from .stdlib import NativeFunction, NativeModule, Handle, create_stdlib
class Env:
    def __init__(self,parent=None): self.parent=parent; self.values={}; self.constants=set()
    def define(self,n,v,const=False):
        if n in self.values: raise RuntimeError(f"重复定义: {n}")
        self.values[n]=v
        if const: self.constants.add(n)
    def get(self,n):
        if n in self.values: return self.values[n]
        if self.parent: return self.parent.get(n)
        raise RuntimeError(f"未定义名称: {n}")
    def set(self,n,v):
        if n in self.values:
            if n in self.constants: raise RuntimeError(f"不能修改常量: {n}")
            self.values[n]=v; return
        if self.parent: return self.parent.set(n,v)
        raise RuntimeError(f"未定义名称: {n}")
class Control(Exception): pass
class ReturnFlow(Control):
    def __init__(self,v): self.value=v
class BreakFlow(Control): pass
class ContinueFlow(Control): pass

@dataclass
class Task:
    """Deterministic task value; execution is eager within a parallel block."""
    name: str
    result: object = None
    error: object = None
    done: bool = False

    def await_result(self):
        if self.error is not None: raise self.error
        return self.result
@dataclass
class Function:
    params:list; body:object; closure:Env; runtime:object
    def __call__(self,*args,**kwargs):
        if kwargs or len(args)!=len(self.params): raise RuntimeError("函数参数数量不匹配")
        if self.runtime.depth>=self.runtime.policy.max_call_depth: raise ResourceLimitError("函数调用深度超限")
        env=Env(self.closure)
        for n,v in zip(self.params,args): env.define(n,v)
        self.runtime.depth+=1
        try:
            try: self.runtime.exec_block(self.body,env)
            except ReturnFlow as r: return r.value
            return None
        finally: self.runtime.depth-=1
class LambdaFunction(Function):
    def __call__(self,*args,**kwargs):
        if kwargs or len(args)!=len(self.params): raise RuntimeError("函数参数数量不匹配")
        env=Env(self.closure)
        for n,v in zip(self.params,args): env.define(n,v)
        return self.runtime.eval(self.body,env)

class LambdaFunction2(Function):
    def __call__(self,*args,**kwargs):
        if kwargs or len(args)!=len(self.params): raise RuntimeError("函数参数数量不匹配")
        env=Env(self.closure)
        for n,v in zip(self.params,args): env.define(n,v)
        return self.runtime.eval(self.body,env)

class Runtime:
    def __init__(self,policy=None,stdout=None,mount_registry=None,allowed_mounts=None, audit_sink=None, audit_callback=None, compiler=None, module_roots=None, wal_path=None, wal=None, audit_context=None):
        self.compiler=compiler; self.module_roots=tuple(Path(x).resolve() for x in (module_roots or ())); self._module_cache={}; self._module_loading=set()
        self.wal = wal if wal is not None else (WriteAheadLog(wal_path) if wal_path is not None else None); self.policy=policy or Policy(); self.budget=Budget(self.policy); self.stdout=stdout or io.StringIO(); self.depth=0; self.task_count=0; self.tasks={}; self.globals=Env(); self.mount_registry=mount_registry; self.allowed_mounts={str(k):set(v) for k,v in (allowed_mounts or {}).items()}; self.requirements={}; self._transactions=[]
        self.audit_sink = audit_sink if audit_sink is not None else audit_callback
        self.audit_context = dict(audit_context or {})
        self._install()
    def _install(self):
        for n,m in create_stdlib(self).items(): self.globals.define(n,m,True)
        def output(*xs):
            text=" ".join(self.stringify(x) for x in xs)+"\n"; self.budget.charge_output(len(text.encode())); self.stdout.write(text)
        builtins={"print":output,"len":len,"string":lambda x:self.stringify(x),"int":int,"float":float,"bool":bool,"range":lambda a,b=None:list(range(a if b is not None else 0,b if b is not None else a)),"arg":lambda n,d=None:self.args.get(n,d)}
        for n,f in builtins.items(): self.globals.define(n,NativeFunction(n,f),True)
    def stringify(self,v):
        if v is None:return "null"
        if v is True:return "true"
        if v is False:return "false"
        return str(v)
    def run(self,program,args=None,bindings=None,source=None,run_id=None):
        """Execute a program and optionally emit one structured audit record."""
        started = time.monotonic(); record_id = run_id or new_run_id(); status = "success"; error = None
        try:
            self.args=dict(args or {})
            for n,v in (bindings or {}).items(): self.globals.define(n,v,True)
            value=None
            for s in program.statements:value=self.execute(s,self.globals)
            main=self.globals.values.get("main")
            if isinstance(main,Function):value=main(self.args)
            return value
        except BaseException as exc:
            status = "failure"; error = {"type": type(exc).__name__, "message": str(exc)}; raise
        finally:
            if self.audit_sink is not None:
                record = AuditRecord(record_id, script_hash(source if source is not None else program), policy_hash(self.policy), status, {"steps": self.budget.steps, "read_bytes": self.budget.read_bytes, "write_bytes": self.budget.write_bytes, "output_bytes": self.budget.output_bytes, "duration_ms": monotonic_ms(started)}, error=error, started_at=time.time() - (time.monotonic() - started), finished_at=time.time(), **self.audit_context)
                sink = self.audit_sink.emit if hasattr(self.audit_sink, "emit") else self.audit_sink
                sink(record)
    def record_undo(self, undo):
        if self._transactions: self._transactions[-1].add(undo)
    def record_operation(self, operation):
        if self._transactions: self._transactions[-1].add_operation(operation)
    def exec_block(self,block,env):
        child=Env(env);value=None
        for s in block.statements:value=self.execute(s,child)
        return value
    def execute(self,n,env):
        if n is None:return None
        self.budget.tick()
        if isinstance(n,A.Block):return self.exec_block(n,env)
        if isinstance(n,A.Let):env.define(n.name,self.eval(n.value,env),n.constant)
        elif isinstance(n,A.Assign):
            old=self.eval(n.target,env);val=self.apply_assign(n.op,old,self.eval(n.value,env));self.assign(n.target,val,env);return val
        elif isinstance(n,A.ExprStmt):return self.eval(n.expr,env)
        elif isinstance(n,A.If):
            c=self.eval(n.condition,env)
            if not isinstance(c,bool):raise RuntimeError("if 条件必须是 Bool",n.span)
            return self.execute(n.then if c else n.otherwise,env)
        elif isinstance(n,A.While):
            loops=0
            while self.eval(n.condition,env):
                loops+=1
                if loops>self.policy.max_loop_iterations:raise ResourceLimitError("循环次数超限",n.span)
                try:self.exec_block(n.body,env)
                except ContinueFlow:continue
                except BreakFlow:break
        elif isinstance(n,A.For):
            for i,v in enumerate(self.eval(n.iterable,env)):
                if i>=self.policy.max_loop_iterations:raise ResourceLimitError("循环次数超限",n.span)
                loop=Env(env);loop.define(n.name,v)
                try:self.exec_block(n.body,loop)
                except ContinueFlow:continue
                except BreakFlow:break
        elif isinstance(n,A.FunctionDecl):env.define(n.name,Function(n.params,n.body,env,self),True)
        elif isinstance(n,A.Return):raise ReturnFlow(self.eval(n.value,env) if n.value else None)
        elif isinstance(n,A.Break):raise BreakFlow()
        elif isinstance(n,A.Continue):raise ContinueFlow()
        elif isinstance(n,A.Throw):raise ScriptThrown(self.eval(n.value,env),n.span)
        elif isinstance(n,A.Parallel):
            if len(n.tasks)>self.policy.max_tasks: raise ResourceLimitError("任务数量超限",n.span)
            for decl in n.tasks:
                if decl.name in self.tasks: raise RuntimeError(f"重复任务: {decl.name}",decl.span)
                task=Task(decl.name); self.tasks[decl.name]=task
                try: task.result=self.exec_block(decl.body,env)
                except ReturnFlow as ret: task.result=ret.value
                except BaseException as exc: task.error=exc
                finally: task.done=True
        elif isinstance(n,A.Transaction):
            tx=TransactionContext(self); self._transactions.append(tx)
            try:
                result=self.exec_block(n.body,env)
            except BaseException:
                try:
                    tx.rollback()
                    if n.rollback: self.exec_block(n.rollback,env)
                finally: self._transactions.pop()
                raise
            else:
                self._transactions.pop()
                tx.commit()
                if self._transactions:
                    self._transactions[-1].undos.extend(tx.undos)
                    self._transactions[-1].operations.extend(tx.operations)
                return result
        elif isinstance(n,A.Try):
            try:self.exec_block(n.body,env)
            except ScriptThrown as e:
                if not n.catch_body:raise
                ce=Env(env);ce.define(n.catch_name or "error",{"message":e.message,"value":e.value});self.exec_block(n.catch_body,ce)
            finally:
                if n.finally_body:self.exec_block(n.finally_body,env)
        elif isinstance(n,A.Assert):
            if not self.eval(n.condition,env):raise RuntimeError(self.eval(n.message,env) if n.message else "断言失败",n.span)
        elif isinstance(n,A.Import):
            module=self.globals.get(n.module[4:]) if n.module.startswith("std.") else self.load_module(n.module,n.span.source,n.span)
            if n.alias in env.values:
                if env.values[n.alias] is not module:raise RuntimeError(f"导入别名冲突: {n.alias}",n.span)
            else:env.define(n.alias,module,True)
        elif isinstance(n,A.Requirement):
            self.requirements[n.name]=(n.kind,set(n.permissions))
        elif isinstance(n,A.Mount):
            if self.mount_registry is None:raise RuntimeError("运行时未配置挂载代理",n.span)
            path=str(self.eval(n.source,env));req=self.requirements.get(n.name)
            if req is None:raise RuntimeError(f"挂载 {n.name} 未在 require 中声明",n.span)
            if req[0]!=n.kind:raise RuntimeError(f"挂载 {n.name} 类型与 require 不一致",n.span)
            allowed=self.allowed_mounts.get(path,set())
            missing=req[1]-allowed
            if missing:raise CapabilityError(f"磁盘 {path} 未授权能力: {', '.join(sorted(missing))}",n.span)
            env.define(n.name,self.mount_registry.open(n.name,path,kind=n.kind,permissions=req[1]),True)
    def load_module(self,spec,importer,span):
        if not (spec.startswith("./") or spec.startswith("../")): raise RuntimeError("仅允许相对模块路径",span)
        path=(Path(importer).parent/spec).resolve()
        if path.suffix != ".vds" or (self.module_roots and not any(path == r or r in path.parents for r in self.module_roots)):
            raise RuntimeError("模块路径不在允许的根目录",span)
        key=str(path)
        if key in self._module_loading: raise RuntimeError("循环导入",span)
        if key in self._module_cache: return self._module_cache[key]
        self._module_loading.add(key)
        try:
            program=self.compiler.compile_file(path) if self.compiler else parse(path.read_text(encoding="utf-8"),key)
            menv=Env(self.globals); exports={}
            for stmt in program.ast.statements:
                self.execute(stmt,menv)
                if isinstance(stmt,(A.Let,A.FunctionDecl)) and stmt.exported: exports[stmt.name]=menv.get(stmt.name)
            self._module_cache[key]=exports
            return exports
        finally:
            self._module_loading.discard(key)
    def eval(self,n,env):
        self.budget.tick()
        if isinstance(n,A.Literal): return n.value
        if isinstance(n,A.Await):
            value=self.tasks.get(n.operand.name) if isinstance(n.operand,A.Name) else self.eval(n.operand,env)
            if not isinstance(value,Task): raise RuntimeError("await 需要 Task",n.span)
            return value.await_result()
        if isinstance(n,A.Lambda): return LambdaFunction(n.params,n.body,env,self)
        if isinstance(n,A.Name): return env.get(n.name)
        if isinstance(n,A.ListExpr): return [self.eval(x,env) for x in n.items]
        if isinstance(n,A.MapExpr): return {k:self.eval(v,env) for k,v in n.items}
        if isinstance(n,A.Unary):
            v=self.eval(n.operand,env)
            if n.op in ("not","!"): return not v
            if n.op=="-": return -v
            if n.op=="+": return +v
        if isinstance(n,A.Binary):
            if n.op=="and": return self.eval(n.left,env) and self.eval(n.right,env)
            if n.op=="or": return self.eval(n.left,env) or self.eval(n.right,env)
            if n.op=="??":
                v=self.eval(n.left,env); return v if v is not None else self.eval(n.right,env)
            a=self.eval(n.left,env)
            if n.op=="|>":
                if isinstance(n.right,A.Call):
                    fn=self.eval(n.right.callee,env); args=[self.eval(x,env) for x in n.right.args]; kwargs={k:self.eval(v,env) for k,v in n.right.kwargs.items()}
                    return fn(a,*args,**kwargs)
                return self.eval(n.right,env)(a)
            b=self.eval(n.right,env)
            if n.op in ("..","..="):
                return list(range(int(a),int(b)+(1 if n.op=="..=" else 0)))
            ops={"+":operator.add,"-":operator.sub,"*":operator.mul,"/":operator.truediv,"%":operator.mod,"==":operator.eq,"!=":operator.ne,"<":operator.lt,"<=":operator.le,">":operator.gt,">=":operator.ge,"in":lambda x,y:x in y}
            try:return ops[n.op](a,b)
            except Exception as exc: raise RuntimeError(f"运算失败 {n.op}: {exc}",n.span)
        if isinstance(n,A.Member): return self.member(self.eval(n.obj,env),n.name,n.span)
        if isinstance(n,A.Index):
            try:return self.eval(n.obj,env)[self.eval(n.index,env)]
            except Exception as exc: raise RuntimeError(f"索引失败: {exc}",n.span)
        if isinstance(n,A.Call):
            fn=self.eval(n.callee,env); args=[self.eval(x,env) for x in n.args]; kwargs={k:self.eval(v,env) for k,v in n.kwargs.items()}
            if not callable(fn): raise RuntimeError("对象不可调用",n.span)
            try:return fn(*args,**kwargs)
            except (RuntimeError,ResourceLimitError,ScriptThrown): raise
            except Exception as exc: raise RuntimeError(f"调用失败: {exc}",n.span,cause=exc)
        if isinstance(n,A.Match):
            subject=self.eval(n.subject,env)
            for arm in n.arms:
                pattern=self.eval(arm.pattern,env)
                if pattern==subject and (arm.guard is None or self.eval(arm.guard,env)): return self.execute(arm.body,env)
            return None
        raise RuntimeError(f"不支持的表达式: {type(n).__name__}",n.span)
    def member(self,obj,name,span):
        if name.startswith("_"): raise RuntimeError("禁止访问私有成员",span)
        if isinstance(obj,NativeModule): return obj.member(name)
        if isinstance(obj,Handle) and name in ("kind","name"): return getattr(obj,name)
        if isinstance(obj,dict): return obj.get(name)
        if isinstance(obj,(list,str,bytes)) and name in ("length","len"): return len(obj)
        raise RuntimeError(f"类型没有成员 {name}",span)
    def assign(self,target,value,env):
        if isinstance(target,A.Name): env.set(target.name,value); return
        if isinstance(target,A.Index): self.eval(target.obj,env)[self.eval(target.index,env)]=value; return
        raise RuntimeError("无效赋值目标",target.span)
    def apply_assign(self,op,a,b):
        return {"=":lambda:b,"+=":lambda:a+b,"-=":lambda:a-b,"*=":lambda:a*b,"/=":lambda:a/b,"%=":lambda:a%b}[op]()
