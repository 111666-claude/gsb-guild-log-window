"""公会操作日志：时间窗口、条数上限与幂等去重，查询用生成器惰性产出。"""

from bisect import bisect_left
from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    """一条公会操作日志。"""

    event_id: str
    actor: str
    action: str
    target: str
    at_ms: int


class Window:
    """日志窗口台账。"""

    def __init__(self, window_ms, limit, min_action_len=2):
        self.window_ms = window_ms
        self.limit = limit
        self.min_action_len = min_action_len
        self.entries = []
        self.invalid = 0
        self.scanned = 0
        self._seen = set()
        self._order = []

    def _valid(self, entry):
        return (
            isinstance(entry.event_id, str)
            and entry.event_id != ""
            and isinstance(entry.actor, str)
            and entry.actor != ""
            and isinstance(entry.target, str)
            and entry.target != ""
            and isinstance(entry.action, str)
            and len(entry.action) >= self.min_action_len
        )

    def add(self, entry):
        """校验字段并按 event_id 去重后入账，超出 limit 时丢掉最旧的一条。"""
        if not self._valid(entry):
            self.invalid += 1
            return False
        if entry.event_id in self._seen:
            return False
        self._seen.add(entry.event_id)
        key = (entry.at_ms, entry.event_id)
        index = bisect_left(self._order, key)
        self._order.insert(index, key)
        self.entries.insert(index, entry)
        if len(self.entries) > self.limit:
            self._order.pop(0)
            self.entries.pop(0)
        return True

    def recent(self, now_ms):
        """惰性产出 [now-window, now] 内的条目，按 at_ms 升序、同刻按 event_id。"""
        lower = now_ms - self.window_ms
        index = bisect_left(self._order, (lower, ""))
        total = len(self.entries)
        while index < total:
            self.scanned += 1
            entry = self.entries[index]
            if entry.at_ms > now_ms:
                break
            yield entry
            index += 1
