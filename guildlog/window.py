"""公会操作日志：时间窗口、条数上限与幂等去重，查询用生成器惰性产出。

缺陷：字段不校验、同一个 event_id 重复记、条数上限不生效、窗口不裁、
产出顺序按插入而不是时间、每次查询全扫日志。
"""

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

    def add(self, entry):
        """记一条日志。缺陷：不校验字段、不查 event_id、不剪上限。"""
        self.entries.append(entry)
        return True

    def recent(self, now_ms):
        """产出窗口内的日志（生成器）。缺陷：不裁窗口、不看上限、按插入顺序、全扫。"""
        self.scanned += len(self.entries)
        for entry in self.entries:
            yield entry
