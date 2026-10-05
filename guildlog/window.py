"""公会操作日志：时间窗口、条数上限与幂等去重，查询用生成器惰性产出。"""

from bisect import insort, bisect_left
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
        self._sorted = []  # 按 (at_ms, event_id) 升序，只保留最近 limit 条
        self._seen = set()
        self.invalid = 0
        self.scanned = 0

    @property
    def entries(self):
        return list(self._sorted)

    def add(self, entry):
        """校验字段并记账；同一 event_id 幂等；超出 limit 丢最旧的。"""
        if (
            not entry.event_id
            or not entry.actor
            or not entry.target
            or len(entry.action) < self.min_action_len
        ):
            self.invalid += 1
            return False
        if entry.event_id in self._seen:
            return False
        self._seen.add(entry.event_id)
        insort(self._sorted, (entry.at_ms, entry.event_id, entry))
        if len(self._sorted) > self.limit:
            self._sorted.pop(0)
        return True

    def recent(self, now_ms):
        """惰性产出 [now-window, now] 内的日志，按 at_ms 升序、同刻按 event_id。"""
        lo = bisect_left(self._sorted, (now_ms - self.window_ms,))
        hi = bisect_left(self._sorted, (now_ms + 1,))
        for _, _, entry in self._sorted[lo:hi]:
            self.scanned += 1
            yield entry
