"""AST nodes for the VScript MVP."""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Any,List,Optional
from .errors import SourceSpan
@dataclass
class Node: span:SourceSpan
@dataclass
class Program(Node): statements:list=field(default_factory=list);language:str="1.0"
@dataclass
class Block(Node): statements:list=field(default_factory=list)
@dataclass
class Literal(Node): value:Any=None
@dataclass
class Name(Node): name:str=""
@dataclass
class ListExpr(Node): items:list=field(default_factory=list)
@dataclass
class MapExpr(Node): items:list=field(default_factory=list)
@dataclass
class Unary(Node): op:str="";operand:Node=None
@dataclass
class Binary(Node): left:Node=None;op:str="";right:Node=None
@dataclass
class Member(Node): obj:Node=None;name:str=""
@dataclass
class Index(Node): obj:Node=None;index:Node=None
@dataclass
class Call(Node): callee:Node=None;args:list=field(default_factory=list);kwargs:dict=field(default_factory=dict)
@dataclass
class Lambda(Node): params:list=field(default_factory=list);body:Node=None
@dataclass
class Let(Node): name:str="";value:Node=None;constant:bool=False;exported:bool=False
@dataclass
class Assign(Node): target:Node=None;op:str="=";value:Node=None
@dataclass
class ExprStmt(Node): expr:Node=None
@dataclass
class If(Node): condition:Node=None;then:Block=None;otherwise:Optional[Node]=None
@dataclass
class While(Node): condition:Node=None;body:Block=None
@dataclass
class For(Node): name:str="";iterable:Node=None;body:Block=None
@dataclass
class FunctionDecl(Node): name:str="";params:list=field(default_factory=list);body:Block=None;exported:bool=False
@dataclass
class Return(Node): value:Optional[Node]=None
@dataclass
class Break(Node): pass
@dataclass
class Continue(Node): pass
@dataclass
class Throw(Node): value:Node=None
@dataclass
class Try(Node): body:Block=None;catch_name:Optional[str]=None;catch_body:Optional[Block]=None;finally_body:Optional[Block]=None
@dataclass
class Assert(Node): condition:Node=None;message:Optional[Node]=None
@dataclass
class Import(Node): module:str="";alias:str=""
@dataclass
class Requirement(Node): name:str="";kind:str="";permissions:list=field(default_factory=list)
@dataclass
class Mount(Node): name:str="";kind:str="";source:Node=None

@dataclass
class MatchArm(Node):
    pattern:Node=None; body:Node=None; guard:Any=None
@dataclass
class Match(Node):
    subject:Node=None; arms:list=field(default_factory=list)

@dataclass
class Transaction(Node):
    """An in-process transaction with runtime-managed undo callbacks."""
    body: Block = None
    rollback: Optional[Block] = None

@dataclass
class TaskDecl(Node):
    name: str = ""
    body: Block = None

@dataclass
class Parallel(Node):
    tasks: list = field(default_factory=list)

@dataclass
class Await(Node):
    operand: Node = None
