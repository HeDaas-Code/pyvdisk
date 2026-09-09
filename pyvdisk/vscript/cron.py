"""Small, dependency-free five-field cron implementation."""
from __future__ import annotations
from datetime import datetime, timedelta

_FIELDS = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
class CronError(ValueError): pass

def _values(text, lo, hi, field):
    result = set()
    for part in text.split(','):
        if not part: raise CronError(f"empty {field} expression")
        bits = part.split('/')
        if len(bits) > 2: raise CronError("too many '/' in cron field")
        try: step = int(bits[1]) if len(bits) == 2 else 1
        except ValueError as exc: raise CronError("cron step must be an integer") from exc
        if step <= 0: raise CronError("cron step must be positive")
        base = bits[0]
        if base == '*': start, end = lo, hi
        elif '-' in base:
            ends = base.split('-')
            if len(ends) != 2: raise CronError("invalid cron range")
            try: start, end = map(int, ends)
            except ValueError as exc: raise CronError("cron value must be an integer") from exc
        else:
            if len(bits) == 2: raise CronError("step requires '*' or a range")
            try: start = end = int(base)
            except ValueError as exc: raise CronError("cron value must be an integer") from exc
        if start < lo or end > hi or start > end: raise CronError(f"cron {field} out of range")
        result.update(range(start, end + 1, step))
    return frozenset(result)

class CronExpression:
    def __init__(self, expression):
        if not isinstance(expression, str): raise CronError("cron expression must be a string")
        parts = expression.split()
        if len(parts) != 5: raise CronError("cron requires five fields")
        self.expression = ' '.join(parts)
        self._sets = tuple(_values(x, *bounds, name) for x, bounds, name in zip(parts, _FIELDS, ('minute','hour','day','month','weekday')))
    def matches(self, value):
        if not isinstance(value, datetime): raise TypeError("matches expects datetime")
        weekday = (value.weekday() + 1) % 7
        return (value.minute in self._sets[0] and value.hour in self._sets[1] and value.day in self._sets[2] and value.month in self._sets[3] and (weekday in self._sets[4] or (weekday == 0 and 7 in self._sets[4])))
    def match(self, value): return self.matches(value)
    def next_after(self, value):
        if not isinstance(value, datetime): raise TypeError("next_after expects datetime")
        candidate = value.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(5 * 366 * 24 * 60):
            if self.matches(candidate): return candidate
            candidate += timedelta(minutes=1)
        raise CronError("cron has no occurrence in search window")
    def __repr__(self): return f"CronExpression({self.expression!r})"

def cron(expression): return CronExpression(expression)
parse_cron = cron
