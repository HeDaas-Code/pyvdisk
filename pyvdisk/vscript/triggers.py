"""Safe local trigger registration and polling primitives.

This module intentionally executes only caller-provided Python callbacks and local
filesystem/log APIs: it has no subprocess, shell, socket, or network support.
"""
from __future__ import annotations
import hashlib, json, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional
from .checkpoint import CheckpointStore

@dataclass(frozen=True)
class Trigger:
    name: str
    kind: str
    pattern: str = ''
    stream: str = ''
    events: tuple = ()
    levels: tuple = ()
    logger: str = ''

def event_position(event):
    """The cursor an event is ordered by.

    ``LogEvent.event_id`` defaults to a random uuid4 hex string, so ordering ids as
    text says nothing about what came later -- it silently dropped about half of the
    events that should have been delivered. ``sequence`` is the monotonic cursor the
    log actually assigns, so that is the position; the id is only a fallback for
    sources that have nothing better.
    """
    sequence = getattr(event, 'sequence', None)
    if sequence is not None:
        return int(sequence)
    return str(getattr(event, 'event_id', getattr(event, 'id', '')))


def is_newer(position, watermark):
    """True when ``position`` is past ``watermark``."""
    try:
        return int(position) > int(watermark)
    except (TypeError, ValueError):
        # Without a sequence the id is all there is, and an id can only be
        # recognised as already delivered when it repeats exactly.
        return str(position) != str(watermark)


class TriggerRegistry:
    def __init__(self, path): self.path=Path(path); self.triggers={}; self._load()
    def _load(self):
        try: raw=json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError: return
        if not isinstance(raw,dict): raise ValueError('invalid trigger registry')
        for item in raw.get('triggers',[]):
            if isinstance(item,dict):
                item['events']=tuple(item.get('events',())); item['levels']=tuple(item.get('levels',()))
                t=Trigger(**{k:item.get(k, getattr(Trigger,k,'')) for k in ('name','kind','pattern','stream','events','levels','logger')}); self.triggers[t.name]=t
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_name('.'+self.path.name+'.tmp')
        tmp.write_text(json.dumps({'version':1,'triggers':[asdict(t) for t in self.triggers.values()]},sort_keys=True),encoding='utf-8'); tmp.replace(self.path)
    def register(self, trigger):
        if not isinstance(trigger,Trigger) or not trigger.name or trigger.kind not in ('file','log'): raise ValueError('invalid trigger')
        # Reject a trigger that could never fire here, where the caller can fix it:
        # an empty file pattern otherwise raises out of the polling loop instead.
        if trigger.kind=='file' and not trigger.pattern: raise ValueError('file trigger requires a pattern')
        if trigger.kind=='log' and not trigger.stream: raise ValueError('log trigger requires a stream')
        self.triggers[trigger.name]=trigger; self.save(); return trigger
    def register_file(self,name,pattern,events=('create','modify','delete')): return self.register(Trigger(name,'file',pattern=pattern,events=tuple(events)))
    def register_log(self,name,stream,levels=(),logger=''): return self.register(Trigger(name,'log',stream=stream,levels=tuple(levels),logger=logger))
    def remove(self,name):
        self.triggers.pop(name,None); self.save()
    def list(self): return tuple(self.triggers.values())

class SchedulerDaemon:
    def __init__(self, registry, checkpoint, *, root='.', log_sources=None, clock=time.time):
        self.registry=registry if isinstance(registry,TriggerRegistry) else TriggerRegistry(registry)
        self.checkpoint=checkpoint if isinstance(checkpoint,CheckpointStore) else CheckpointStore(checkpoint)
        self.root=Path(root); self.log_sources=log_sources or {}; self.clock=clock; self._snapshots={}
    def _file_events(self,t):
        current={str(p.relative_to(self.root)): (p.stat().st_mtime_ns,p.stat().st_size) for p in self.root.glob(t.pattern) if p.is_file()}
        old=self._snapshots.get(t.name,{ }); self._snapshots[t.name]=current
        for p in sorted(set(current)|set(old)):
            typ='create' if p in current and p not in old else 'delete' if p in old and p not in current else 'modify'
            if typ in t.events and (typ!='modify' or current.get(p)!=old.get(p)): yield {'id':f'{t.name}:{typ}:{p}:{current.get(p,old.get(p))}','path':p,'event':typ}
    def _log_events(self,t):
        source=self.log_sources.get(t.name,self.log_sources.get(t.stream))
        if source is None: return ()
        after=self.checkpoint.last_event(t.name)
        events=source.query(t.stream, levels=list(t.levels) or None, loggers=[t.logger] if t.logger else None) if hasattr(source,'query') else source(t)
        out=[]
        for e in events:
            position=event_position(e)
            if after is not None and not is_newer(position,after): continue
            out.append((position,e))
        return out
    def poll_once(self, handlers):
        delivered=0
        for t in self.registry.list():
            items=((x['id'],x) for x in self._file_events(t)) if t.kind=='file' else self._log_events(t)
            for eid,event in items:
                # checkpoint is intentionally written after handler: at-least-once on failure.
                handlers[t.name](event)
                self.checkpoint.mark_success(t.name,eid); delivered+=1
        return delivered
    def run(self, handlers, *, interval=1.0, stop_event=None):
        while stop_event is None or not stop_event.is_set():
            self.poll_once(handlers); time.sleep(interval)

Daemon=SchedulerDaemon
register_file_trigger=lambda registry,name,pattern,events=('create','modify','delete'): registry.register_file(name,pattern,events)
register_log_trigger=lambda registry,name,stream,levels=(),logger='': registry.register_log(name,stream,levels,logger)
