"""统一结构化日志基础组件。"""
from __future__ import annotations
import contextlib, contextvars, logging, threading, time, traceback, uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

_context = contextvars.ContextVar("pyvdisk_log_context", default={})
LEVELS = {"TRACE": 5, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
logging.addLevelName(5, "TRACE")

def normalize_level(level: Any) -> str:
    if isinstance(level, int): return logging.getLevelName(level).upper()
    value = str(level).upper()
    if value == "WARN": value = "WARNING"
    if value not in LEVELS: raise ValueError(f"未知日志级别: {level}")
    return value

@dataclass
class LogEvent:
    timestamp_ns: int
    level: str
    logger: str
    message: str
    fields: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    exception: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    thread: Optional[str] = None
    # Optional Agentic event-trace metadata; sequence is assigned per stream.
    sequence: Optional[int] = None
    schema_version: Optional[str] = None
    run_id: Optional[str] = None
    task_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def __post_init__(self): self.level = normalize_level(self.level)
    def to_dict(self):
        return {"timestamp_ns": self.timestamp_ns, "level": self.level, "logger": self.logger,
                "message": self.message, "fields": self.fields, "tags": self.tags,
                "event_id": self.event_id, "exception": self.exception,
                "trace_id": self.trace_id, "span_id": self.span_id, "thread": self.thread,
                "sequence": self.sequence, "schema_version": self.schema_version,
                "run_id": self.run_id, "task_id": self.task_id,
                "correlation_id": self.correlation_id}
    @classmethod
    def from_dict(cls, value): return cls(**value)

@contextlib.contextmanager
def log_context(**values):
    merged = dict(_context.get()); merged.update(values); token = _context.set(merged)
    try: yield merged
    finally: _context.reset(token)

def bind_context(**values):
    merged = dict(_context.get()); merged.update(values); _context.set(merged); return merged

def clear_context(): _context.set({})

class LogSink:
    def emit(self, event: LogEvent): raise NotImplementedError
    def flush(self): pass
    def close(self): pass

class MemorySink(LogSink):
    def __init__(self, capacity=10000): self.capacity=capacity; self.events=[]; self._lock=threading.Lock()
    def emit(self,event):
        with self._lock:
            self.events.append(event)
            if len(self.events)>self.capacity: del self.events[:-self.capacity]

class StreamSink(LogSink):
    def __init__(self, stream=None):
        import sys; self.stream=stream or sys.stderr
    def emit(self,event):
        import json; self.stream.write(json.dumps(event.to_dict(),ensure_ascii=False)+"\n"); self.stream.flush()

class LogDiskSink(LogSink):
    def __init__(self, disk, stream="default"): self.disk=disk; self.stream=stream
    def emit(self,event): self.disk.append(self.stream,event)

class UnifiedLogger:
    def __init__(self,name:str,sinks:Optional[Iterable[LogSink]]=None,level="INFO",fields=None,tags=None):
        self.name=name; self.sinks=list(sinks or []); self.level=LEVELS[normalize_level(level)]
        self.fields=dict(fields or {}); self.tags=dict(tags or {})
    def bind(self,**fields): return UnifiedLogger(self.name,self.sinks,self.level,self.fields|fields,self.tags)
    def with_tags(self,**tags): return UnifiedLogger(self.name,self.sinks,self.level,self.fields,self.tags|{k:str(v) for k,v in tags.items()})
    def log(self,level,message,*,fields=None,tags=None,exc_info=None,timestamp_ns=None):
        lvl=normalize_level(level)
        if LEVELS[lvl] < self.level: return None
        ctx=dict(_context.get()); trace_id=ctx.pop("trace_id",None); span_id=ctx.pop("span_id",None)
        merged=self.fields|ctx|dict(fields or {}); merged_tags=self.tags|{k:str(v) for k,v in (tags or {}).items()}
        exception=None
        if exc_info:
            if exc_info is True: exception=traceback.format_exc()
            elif isinstance(exc_info,BaseException): exception="".join(traceback.format_exception(exc_info))
            else: exception=str(exc_info)
        event=LogEvent(timestamp_ns or time.time_ns(),lvl,self.name,str(message),merged,merged_tags,
                       exception=exception,trace_id=trace_id,span_id=span_id,thread=threading.current_thread().name)
        for sink in self.sinks: sink.emit(event)
        return event
    def trace(self,m,**kw): return self.log("TRACE",m,**kw)
    def debug(self,m,**kw): return self.log("DEBUG",m,**kw)
    def info(self,m,**kw): return self.log("INFO",m,**kw)
    def warning(self,m,**kw): return self.log("WARNING",m,**kw)
    warn=warning
    def error(self,m,**kw): return self.log("ERROR",m,**kw)
    def critical(self,m,**kw): return self.log("CRITICAL",m,**kw)
    def exception(self,m,**kw): kw["exc_info"]=True; return self.error(m,**kw)

class StandardLoggingHandler(logging.Handler):
    def __init__(self,sink:LogSink,stream="default",level=logging.NOTSET): super().__init__(level); self.sink=sink; self.stream=stream
    def emit(self,record):
        try:
            fields={k:v for k,v in record.__dict__.items() if k not in _STANDARD_RECORD_FIELDS}
            event=LogEvent(int(record.created*1_000_000_000),record.levelname,record.name,record.getMessage(),fields,
                           exception=self.formatException(record.exc_info) if record.exc_info else None,
                           thread=record.threadName)
            self.sink.emit(event)
        except Exception: self.handleError(record)

_STANDARD_RECORD_FIELDS=set(logging.makeLogRecord({}).__dict__)|{"message","asctime"}

def get_logger(name:str,*sinks:LogSink,level="INFO",**fields): return UnifiedLogger(name,sinks,level,fields)
