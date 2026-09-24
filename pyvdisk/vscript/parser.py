"""Recursive-descent statements plus Pratt expressions."""
from .tokens import TokenType as T
from .lexer import lex
from .errors import ParseError,SourceSpan
from . import ast as A
PREC={T.PIPE:1,T.COALESCE:2,T.OR:3,T.AND:4,T.EQ:5,T.NE:5,T.IN:6,T.LT:6,T.LE:6,T.GT:6,T.GE:6,T.RANGE:7,T.RANGE_INCLUSIVE:7,T.PLUS:8,T.MINUS:8,T.STAR:9,T.SLASH:9,T.PERCENT:9}
ASSIGN={T.ASSIGN:"=",T.PLUS_ASSIGN:"+=",T.MINUS_ASSIGN:"-=",T.STAR_ASSIGN:"*=",T.SLASH_ASSIGN:"/=",T.PERCENT_ASSIGN:"%="}
class Parser:
 def __init__(self,tokens):self.ts=tokens;self.i=0
 def cur(self):return self.ts[self.i]
 def span(self,t=None):
  t=t or self.cur();return SourceSpan(t.line,t.column,t.line,t.column+max(1,len(t.lexeme)),t.source)
 def match(self,*types):
  if self.cur().type in types:t=self.cur();self.i+=1;return t
  return None
 def need(self,typ,msg=None):
  t=self.match(typ)
  if not t:raise ParseError(msg or f"期望 {typ.value}，实际 {self.cur().lexeme or 'EOF'}",self.span())
  return t
 def parse(self):
  language="1.0";statements=[];start=self.span()
  if self.match(T.LANGUAGE):language=self.need(T.STRING,"language 后需要版本字符串").value;self.need(T.SEMICOLON)
  while self.cur().type!=T.EOF:statements.append(self.statement())
  return A.Program(start,statements,language)
 def statement(self):
  t=self.cur()
  if self.match(T.LET):return self.let(t,False)
  if self.match(T.CONST):return self.let(t,True)
  if self.match(T.EXPORT):
   if self.match(T.FN):return self.function(t,True)
   if self.match(T.LET):return self.let(t,False,True)
   if self.match(T.CONST):return self.let(t,True,True)
   raise ParseError("export 仅支持 fn/let/const",self.span(t))
  if self.match(T.IF):return self.ifstmt(t)
  if self.match(T.MATCH):return self.matchstmt(t)
  if self.match(T.WHILE):
   c=self.expr();b=self.block();return A.While(self.span(t),c,b)
  if self.match(T.FOR):
   n=self.need(T.IDENT,"for 需要循环变量").value;self.need(T.IN);it=self.expr();return A.For(self.span(t),n,it,self.block())
  if self.match(T.FN):return self.function(t)
  if self.match(T.RETURN):
   v=None if self.cur().type==T.SEMICOLON else self.expr();self.need(T.SEMICOLON);return A.Return(self.span(t),v)
  if self.match(T.BREAK):self.need(T.SEMICOLON);return A.Break(self.span(t))
  if self.match(T.CONTINUE):self.need(T.SEMICOLON);return A.Continue(self.span(t))
  if self.match(T.THROW):v=self.expr();self.need(T.SEMICOLON);return A.Throw(self.span(t),v)
  if self.match(T.TRY):return self.trystmt(t)
  if self.match(T.TRANSACTION):return self.transaction(t)
  if self.match(T.PARALLEL):return self.parallel(t)
  if self.match(T.IMPORT):return self.importstmt(t)
  if self.match(T.REQUIRE):return self.requirestmt(t)
  if self.match(T.MOUNT):return self.mountstmt(t)
  if self.match(T.ASSERT) or (t.type==T.IDENT and t.value=="assert"):
   if t.type==T.IDENT:self.i+=1
   c=self.expr();m=None
   if self.match(T.COMMA):m=self.expr()
   self.need(T.SEMICOLON);return A.Assert(self.span(t),c,m)
  if t.type==T.LBRACE:return self.block()
  e=self.expr()
  if self.cur().type in ASSIGN:
   op=ASSIGN[self.cur().type];self.i+=1;v=self.expr();self.need(T.SEMICOLON);return A.Assign(self.span(t),e,op,v)
  self.need(T.SEMICOLON);return A.ExprStmt(self.span(t),e)
 def let(self,t,const,exported=False):
  n=self.need(T.IDENT).value
  if self.match(T.COLON):self.need(T.IDENT)
  self.need(T.ASSIGN);v=self.expr();self.need(T.SEMICOLON);return A.Let(self.span(t),n,v,const,exported)
 def block(self):
  t=self.need(T.LBRACE);items=[]
  while self.cur().type not in (T.RBRACE,T.EOF):items.append(self.statement())
  self.need(T.RBRACE,"块缺少 }");return A.Block(self.span(t),items)
 def matchstmt(self,t):
  subject=self.expr();self.need(T.LBRACE);arms=[]
  while self.cur().type not in (T.RBRACE,T.EOF):
   pat=self.expr();guard=None
   if self.match(T.IF):guard=self.expr()
   self.need(T.FAT_ARROW,"match 分支需要 =>")
   body=self.block();arms.append(A.MatchArm(self.span(t),pat,body,guard))
  self.need(T.RBRACE,"match 缺少 }");return A.Match(self.span(t),subject,arms)
 def ifstmt(self,t):
  c=self.expr();then=self.block();other=None
  if self.match(T.ELSE):
   if self.match(T.IF):other=self.ifstmt(self.ts[self.i-1])
   else:other=self.block()
  return A.If(self.span(t),c,then,other)
 def function(self,t,exported=False):
  n=self.need(T.IDENT,"fn 需要名称").value;self.need(T.LPAREN);params=[]
  if self.cur().type!=T.RPAREN:
   while True:
    p=self.need(T.IDENT).value
    if self.match(T.COLON):self.need(T.IDENT)
    params.append(p)
    if not self.match(T.COMMA):break
  self.need(T.RPAREN)
  if self.match(T.ARROW):self.need(T.IDENT)
  return A.FunctionDecl(self.span(t),n,params,self.block(),exported)
 def importstmt(self,t):
  if self.cur().type==T.STRING:module=self.cur().value;self.i+=1
  else:
   parts=[self.need(T.IDENT,"import 需要模块名").value]
   while self.match(T.DOT):parts.append(self.need(T.IDENT).value)
   module=".".join(parts)
  self.need(T.AS,"import 需要 as 别名");alias=self.need(T.IDENT).value;self.need(T.SEMICOLON)
  return A.Import(self.span(t),module,alias)
 def requirestmt(self,t):
  self.need(T.LBRACE);items=[]
  while self.cur().type!=T.RBRACE:
   self.need(T.MOUNT,"require 块目前仅支持 mount")
   name=self.need(T.IDENT).value;self.need(T.COLON);kind=self.need(T.IDENT).value;perms=[]
   while self.cur().type!=T.SEMICOLON:
    perms.append(self.need(T.IDENT,"需要权限名").value)
    if not self.match(T.COMMA):break
   self.need(T.SEMICOLON);items.append(A.Requirement(self.span(t),name,kind,perms))
  self.need(T.RBRACE);return A.Block(self.span(t),items)
 def mountstmt(self,t):
  kind=self.need(T.IDENT,"mount 需要磁盘类型").value;name=self.need(T.IDENT,"mount 需要名称").value;self.need(T.FROM);source=self.expr();self.need(T.SEMICOLON)
  return A.Mount(self.span(t),name,kind,source)
 def parallel(self,t):
  self.need(T.LBRACE,"parallel 需要块")
  tasks=[]
  while self.cur().type not in (T.RBRACE,T.EOF):
   self.need(T.TASK,"parallel 块只能包含 task")
   name=self.need(T.IDENT,"task 需要名称").value
   tasks.append(A.TaskDecl(self.span(t),name,self.block()))
  self.need(T.RBRACE,"parallel 缺少 }")
  return A.Parallel(self.span(t),tasks)
 def transaction(self,t):
  body=self.block();rb=None
  if self.match(T.ON):
   self.need(T.ROLLBACK,"on 后需要 rollback")
   rb=self.block()
  return A.Transaction(self.span(t),body,rb)
 def trystmt(self,t):
  body=self.block();name=None;cb=None;fb=None
  if self.match(T.CATCH):
   self.match(T.LPAREN);name=self.need(T.IDENT).value
   if self.match(T.COLON):self.need(T.IDENT)
   self.match(T.RPAREN);cb=self.block()
  if self.match(T.FINALLY):fb=self.block()
  if cb is None and fb is None:raise ParseError("try 需要 catch 或 finally",self.span(t))
  return A.Try(self.span(t),body,name,cb,fb)
 def expr(self,minp=0):
  t=self.cur();self.i+=1
  if t.type in (T.INT,T.FLOAT,T.STRING,T.BYTES,T.TRUE,T.FALSE,T.NULL):left=A.Literal(self.span(t),t.value)
  elif t.type==T.FN:
   self.need(T.LPAREN);params=[]
   if self.cur().type!=T.RPAREN:
    while True:
     params.append(self.need(T.IDENT).value)
     if not self.match(T.COMMA):break
   self.need(T.RPAREN);self.need(T.ARROW);left=A.Lambda(self.span(t),params,self.expr(0))
  elif t.type==T.IDENT:left=A.Name(self.span(t),t.value)
  elif t.type==T.AWAIT:left=A.Await(self.span(t),self.expr(9))
  elif t.type==T.BAR:
   params=[]
   if self.cur().type!=T.BAR:
    while True:
     params.append(self.need(T.IDENT).value)
     if not self.match(T.COMMA):break
   self.need(T.BAR);left=A.Lambda(self.span(t),params,self.expr(0))
  elif t.type==T.LPAREN:left=self.expr();self.need(T.RPAREN)
  elif t.type==T.LBRACKET:
   items=[]
   if self.cur().type!=T.RBRACKET:
    while True:
     items.append(self.expr())
     if not self.match(T.COMMA):break
   self.need(T.RBRACKET);left=A.ListExpr(self.span(t),items)
  elif t.type==T.LBRACE:
   items=[]
   if self.cur().type!=T.RBRACE:
    while True:
     k=self.cur();self.i+=1
     if k.type not in (T.STRING,T.IDENT):raise ParseError("Map 键必须是字符串或标识符",self.span(k))
     self.need(T.COLON);items.append((k.value,self.expr()))
     if not self.match(T.COMMA):break
   self.need(T.RBRACE);left=A.MapExpr(self.span(t),items)
  elif t.type in (T.NOT,T.BANG,T.MINUS,T.PLUS):left=A.Unary(self.span(t),t.lexeme,self.expr(9))
  else:raise ParseError(f"无效表达式: {t.lexeme or 'EOF'}",self.span(t))
  while True:
   if self.match(T.LPAREN):
    args=[];kwargs={}
    if self.cur().type!=T.RPAREN:
     while True:
      if self.cur().type==T.IDENT and self.ts[self.i+1].type==T.COLON:
       key=self.cur().value;self.i+=2;kwargs[key]=self.expr()
      else:args.append(self.expr())
      if not self.match(T.COMMA):break
    self.need(T.RPAREN);left=A.Call(left.span,left,args,kwargs);continue
   if self.match(T.DOT):left=A.Member(left.span,left,self.need(T.IDENT).value);continue
   if self.match(T.OPTIONAL_DOT):left=A.OptionalMember(left.span,left,self.need(T.IDENT).value);continue
   if self.match(T.LBRACKET):idx=self.expr();self.need(T.RBRACKET);left=A.Index(left.span,left,idx);continue
   typ=self.cur().type;p=PREC.get(typ,-1)
   if p<minp:break
   op=self.cur().lexeme;self.i+=1;right=self.expr(p+1);left=A.Binary(left.span,left,op,right)
  return left

def parse(source,filename="<script>"):return Parser(lex(source,filename)).parse()