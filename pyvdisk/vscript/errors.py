"""VScript source diagnostics, spans, and parse/lex errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class SourceSpan:
    line: int = 1
    column: int = 1
    end_line: int = 1
    end_column: int = 1
    source: str = "<script>"
    start_offset: int = 0
    end_offset: int = 0

    @classmethod
    def zero(cls) -> "SourceSpan":
        return cls()

    def __str__(self) -> str:
        return f"{self.source}:{self.line}:{self.column}"


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str
    line: int = 1
    column: int = 1
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    filename: str = "<script>"
    severity: str = "error"
    notes: tuple = field(default_factory=tuple)

    def format(self) -> str:
        end = ""
        if self.end_line is not None and self.end_line != self.line:
            end = f"-{self.end_line}"
        return (
            f"{self.filename}:{self.line}:{self.column}{end}: "
            f"{self.severity}[{self.code}]: {self.message}"
        )

    def __str__(self) -> str:
        return self.format()


class VScriptError(Exception):
    base_code = "VSCRIPT_ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        span: Optional[SourceSpan] = None,
        *,
        cause: Optional[BaseException] = None,
        details: Optional[dict] = None,
        diagnostic: Optional[Diagnostic] = None,
        code: Optional[str] = None,
    ) -> None:
        if diagnostic is not None:
            message = diagnostic.message
            span = SourceSpan(
                line=diagnostic.line,
                column=diagnostic.column,
                end_line=diagnostic.end_line or diagnostic.line,
                end_column=diagnostic.end_column or diagnostic.column,
                source=diagnostic.filename,
            )
            code = code or diagnostic.code
        self.message = str(message)
        self.span = span
        self.cause = cause
        self.details = details or {}
        self.code = code or self.base_code
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.span is not None:
            return f"{self.span}: {self.message}"
        return self.message

    @property
    def diagnostic(self) -> Diagnostic:
        if self.span is None:
            return Diagnostic(
                code=self.code,
                message=self.message,
                filename="<script>",
            )
        return Diagnostic(
            code=self.code,
            message=self.message,
            line=self.span.line,
            column=self.span.column,
            end_line=self.span.end_line,
            end_column=self.span.end_column,
            filename=self.span.source,
        )


class LexError(VScriptError):
    base_code = "LEX_ERROR"


class ParseError(VScriptError):
    base_code = "PARSE_ERROR"


class CompileError(VScriptError):
    base_code = "COMPILE_ERROR"


class RuntimeError(VScriptError):
    base_code = "RUNTIME_ERROR"


class CapabilityError(RuntimeError):
    base_code = "CAPABILITY_ERROR"


class ResourceLimitError(RuntimeError):
    base_code = "RESOURCE_LIMIT"


class ScriptThrown(RuntimeError):
    def __init__(self, value: Any, span: Optional[SourceSpan] = None) -> None:
        self.value = value
        super().__init__(str(value), span)
