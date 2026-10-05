"""从 jsonl 回放公会日志并打印窗口结果。"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guildlog.window import Entry, Window  # noqa: E402


def build_parser():
    parser = argparse.ArgumentParser(prog="guild-log-window", description="公会日志窗口")
    parser.add_argument("--sample", default="invalid", help="invalid / dup / limit / order / work")
    parser.add_argument("--input", default=None, help="jsonl 日志文件")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    window = Window(1000, 2)
    if args.sample == "invalid":
        window.add(Entry("e1", "p1", "", "p2", 0))
        print("accepted=%d invalid=%d" % (len(list(window.recent(0))), window.invalid))
    elif args.sample == "dup":
        window.add(Entry("e1", "p1", "kick", "p2", 0))
        window.add(Entry("e1", "p1", "kick", "p3", 1))
        print("events=%d" % len(list(window.recent(1))))
    elif args.sample == "limit":
        for index in range(3):
            window.add(Entry("e-%d" % index, "p1", "kick", "p2", index))
        print("events=%d" % len(list(window.recent(2))))
    elif args.sample == "order":
        window.add(Entry("e1", "p1", "kick", "p2", 50))
        window.add(Entry("e2", "p1", "kick", "p3", 10))
        print("first=%s" % next(window.recent(50)).event_id)
    elif args.sample == "work":
        for index in range(3000):
            window.add(Entry("e-%d" % index, "p1", "kick", "p2", index))
        for index in range(3000):
            list(window.recent(2999))
        print("scanned=%d" % window.scanned)
    elif args.input:
        with open(args.input, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    window.add(Entry(**json.loads(line)))
        for entry in window.recent(10 ** 9):
            print("%s %s %s" % (entry.event_id, entry.action, entry.target))
    else:
        raise SystemExit("需要 --sample invalid|dup|limit|order|work，或 --input 文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
