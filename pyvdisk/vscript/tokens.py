"""VScript token types and token records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TokenType(str, Enum):
    """Every lexical token the VScript front end can produce."""

    EOF = "eof"
    IDENT = "ident"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BYTES = "bytes"
    ASSERT = "assert"

    # Keywords
    LANGUAGE = "language"
    LET = "let"
    CONST = "const"
    IF = "if"
    ELSE = "else"
    FOR = "for"
    IN = "in"
    WHILE = "while"
    FN = "fn"
    RETURN = "return"
    BREAK = "break"
    CONTINUE = "continue"
    TRY = "try"
    CATCH = "catch"
    FINALLY = "finally"
    THROW = "throw"
    NOT = "not"
    AND = "and"
    OR = "or"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    IMPORT = "import"
    EXPORT = "export"
    AS = "as"
    REQUIRE = "require"
    MOUNT = "mount"
    FROM = "from"
    MATCH = "match"
    TRANSACTION = "transaction"
    ON = "on"
    ROLLBACK = "rollback"
    PARALLEL = "parallel"
    TASK = "task"
    AWAIT = "await"

    # Punctuation
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    DOT = "."
    QUESTION = "?"
    ARROW = "->"
    FAT_ARROW = "=>"
    RANGE = ".."
    RANGE_INCLUSIVE = "..="
    COALESCE = "??"
    PIPE = "|>"
    OPTIONAL_DOT = "?."
    BAR = "|"

    # Operators
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    STAR_ASSIGN = "*="
    SLASH_ASSIGN = "/="
    PERCENT_ASSIGN = "%="
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    BANG = "!"


KEYWORDS: dict[str, TokenType] = {
    "language": TokenType.LANGUAGE,
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "while": TokenType.WHILE,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
    "throw": TokenType.THROW,
    "not": TokenType.NOT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "import": TokenType.IMPORT,
    "export": TokenType.EXPORT,
    "as": TokenType.AS,
    "require": TokenType.REQUIRE,
    "mount": TokenType.MOUNT,
    "from": TokenType.FROM,
    "match": TokenType.MATCH,
    "transaction": TokenType.TRANSACTION,
    "on": TokenType.ON,
    "rollback": TokenType.ROLLBACK,
    "parallel": TokenType.PARALLEL,
    "task": TokenType.TASK,
    "await": TokenType.AWAIT,
    "assert": TokenType.ASSERT,
}

# Literal keywords carry a useful Python value in the token.
KEYWORD_VALUES: dict[TokenType, Any] = {
    TokenType.TRUE: True,
    TokenType.FALSE: False,
    TokenType.NULL: None,
}


@dataclass
class Token:
    type: TokenType
    lexeme: str
    value: Any = None
    line: int = 1
    column: int = 1
    source: str = "<script>"
    offset: int = 0
    end_offset: int = 0

    def __repr__(self) -> str:
        return (
            f"Token({self.type.value!r}, {self.lexeme!r}, {self.value!r}, "
            f"{self.line}:{self.column})"
        )

    @property
    def is_eof(self) -> bool:
        return self.type is TokenType.EOF
