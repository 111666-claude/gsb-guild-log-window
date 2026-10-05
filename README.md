# guild-log-window

公会操作日志：时间窗口、条数上限与幂等去重，查询用生成器惰性产出，日志从 jsonl 回放，只用 Python 标准库。

```
python3 replay.py --sample=invalid
python3 replay.py --sample=dup
python3 replay.py --sample=limit
python3 replay.py --sample=order
python3 replay.py --sample=work
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **字段校验**：`event_id`、`actor`、`target` 非空且 `action` 长度不小于 `min_action_len`，
  否则记进 `invalid` 且不入账。
- **幂等**：同一个 `event_id` 只记一次，重复上报不改变台账。
- **条数上限**：最多保留最近 `limit` 条，超出时丢掉最旧的。
- **时间窗口**：`recent` 只产出 `[now-window, now]` 内的条目（含边界），按 `at_ms` 升序，同刻按 event_id。
- **惰性**：`recent` 是生成器，调用时不产出，迭代时才计算。
- **代价**：产出不许全扫全部日志，`scanned` 不随日志数乘查询次数增长；10 万条日志每秒 10 万次查询。

## 输出契约（不改格式）

```
accepted=.. invalid=..
events=..
first=..
scanned=..
```

## 目录

```
guildlog/window.py  字段校验、上限、窗口与生成器
replay.py           jsonl 回放入口
tests/test_window.py unittest 用例
```
