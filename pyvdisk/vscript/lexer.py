"""Single-pass maximal-munch VScript lexer."""
from __future__ import annotations
from .tokens import Token, TokenType, KEYWORDS, KEYWORD_VALUES
from .errors import LexError, SourceSpan

class Lexer:
    def __init__(self, source, filename="<script>"):
        self.s, self.file, self.i, self.line, self.col = source, filename, 0, 1, 1
    def span(self, line=None, col=None):
        return SourceSpan(line or self.line, col or self.col, line or self.line, col or self.col, self.file)
    def peek(self, n=0):
        return self.s[self.i+n] if self.i+n < len(self.s) else "\0"
    def advance(self):
        c = self.peek(); self.i += 1
        if c == "\n": self.line += 1; self.col = 1
        else: self.col += 1
        return c
    def token(self, typ, start, line, col, value=None):
        return Token(typ, self.s[start:self.i], value, line, col, self.file, start, self.i)
    def scan(self):
        out = []
        while self.i < len(self.s):
            c = self.peek()
            if c.isspace(): self.advance(); continue
            if c == "#" or (c == "/" and self.peek(1) == "/"):
                while self.peek() not in ("\n", "\0"): self.advance()
                continue
            if c == "/" and self.peek(1) == "*":
                line, col = self.line, self.col; self.advance(); self.advance(); depth = 1
                while depth:
                    if self.peek() == "\0": raise LexError("未结束的块注释", self.span(line, col))
                    if self.peek() == "/" and self.peek(1) == "*": self.advance(); self.advance(); depth += 1
                    elif self.peek() == "*" and self.peek(1) == "/": self.advance(); self.advance(); depth -= 1
                    else: self.advance()
                continue
            start, line, col = self.i, self.line, self.col
            if (c.isalpha() or c == "_") and not (c in "rRbB" and self.peek(1) in "\"'"):
                while self.peek().isalnum() or self.peek() == "_": self.advance()
                text = self.s[start:self.i]; typ = KEYWORDS.get(text, TokenType.IDENT)
                out.append(self.token(typ, start, line, col, KEYWORD_VALUES.get(typ, text))); continue
            if c.isdigit():
                if c == "0" and self.peek(1) in "xXbBoO":
                    base = {"x":16,"b":2,"o":8}[self.peek(1).lower()]; self.advance(); self.advance(); begin = self.i
                    allowed = "0123456789abcdefABCDEF" if base == 16 else "01" if base == 2 else "01234567"
                    while self.peek() in allowed or self.peek() == "_": self.advance()
                    if self.i == begin: raise LexError("无效整数", self.span(line, col))
                    out.append(self.token(TokenType.INT, start, line, col, int(self.s[start:self.i].replace("_", ""), base))); continue
                while self.peek().isdigit() or self.peek() == "_": self.advance()
                floating = False
                if self.peek() == "." and self.peek(1) != ".":
                    floating = True; self.advance()
                    while self.peek().isdigit() or self.peek() == "_": self.advance()
                if self.peek() in "eE":
                    floating = True; self.advance()
                    if self.peek() in "+-": self.advance()
                    if not self.peek().isdigit(): raise LexError("无效浮点数", self.span(line, col))
                    while self.peek().isdigit() or self.peek() == "_": self.advance()
                raw = self.s[start:self.i].replace("_", "")
                out.append(self.token(TokenType.FLOAT if floating else TokenType.INT, start, line, col, float(raw) if floating else int(raw))); continue
            prefix = ""
            if c in "rRbB" and self.peek(1) in "\"'":
                prefix = self.advance().lower(); c = self.peek()
            if c in "\"'":
                quote = self.advance(); chars = []
                while self.peek() != quote:
                    if self.peek() in ("\0", "\n"): raise LexError("未结束的字符串", self.span(line, col))
                    x = self.advance()
                    if x == "\\" and prefix != "r":
                        esc = self.advance(); mapping = {"n":"\n","t":"\t","r":"\r","0":"\0","\\":"\\","\"":"\"","'":"'"}
                        if esc not in mapping: raise LexError(f"不支持的转义: \\{esc}", self.span(self.line, self.col-1))
                        x = mapping[esc]
                    chars.append(x)
                self.advance(); value = "".join(chars)
                out.append(self.token(TokenType.BYTES if prefix == "b" else TokenType.STRING, start, line, col, value.encode("latin-1") if prefix == "b" else value)); continue
            ops = [("..=",TokenType.RANGE_INCLUSIVE),("?.",TokenType.OPTIONAL_DOT),("??",TokenType.COALESCE),("|>",TokenType.PIPE),("=>",TokenType.FAT_ARROW),("->",TokenType.ARROW),("==",TokenType.EQ),("!=",TokenType.NE),("<=",TokenType.LE),(">=",TokenType.GE),("+=",TokenType.PLUS_ASSIGN),("-=",TokenType.MINUS_ASSIGN),("*=",TokenType.STAR_ASSIGN),("/=",TokenType.SLASH_ASSIGN),("%=",TokenType.PERCENT_ASSIGN),("..",TokenType.RANGE)]
            for text, typ in ops:
                if self.s.startswith(text, self.i):
                    for _ in text: self.advance()
                    out.append(self.token(typ, start, line, col)); break
            else:
                single = {"(":TokenType.LPAREN,")":TokenType.RPAREN,"{":TokenType.LBRACE,"}":TokenType.RBRACE,"[":TokenType.LBRACKET,"]":TokenType.RBRACKET,",":TokenType.COMMA,";":TokenType.SEMICOLON,":":TokenType.COLON,".":TokenType.DOT,"?":TokenType.QUESTION,"=":TokenType.ASSIGN,"|":TokenType.BAR,"+":TokenType.PLUS,"-":TokenType.MINUS,"*":TokenType.STAR,"/":TokenType.SLASH,"%":TokenType.PERCENT,"!":TokenType.BANG,"<":TokenType.LT,">":TokenType.GT}
                if c not in single: raise LexError(f"非法字符: {c}", self.span(line, col))
                self.advance(); out.append(self.token(single[c], start, line, col))
        out.append(Token(TokenType.EOF, "", None, self.line, self.col, self.file, self.i, self.i)); return out

def lex(source, filename="<script>"):
    return Lexer(source, filename).scan()
