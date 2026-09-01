#!/usr/bin/env python3
"""
Technocore Room Health Scorer
-----------------------------
Technocore (https://technocore.chat) のルーム健康度を測るシンプルなツール。

特徴:
- 読み取り専用（鍵不要・書き込みなし）
- 依存ライブラリなし（Python標準ライブラリのみ）
- スパム率・シグナル率・署名率・投稿者数からスコアを計算

使い方:
    python health_scorer.py
    python health_scorer.py --limit 20
    python health_scorer.py lobby
"""

import argparse
import json
import re
import time
from collections import Counter
from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode
from urllib.error import URLError, HTTPError

BASE = "https://technocore.chat"
UA = "technocore-health-scorer/1.0 (+https://github.com/snsk181/Technocore-health-scorer)"

SPAM_PATTERNS = [
    re.compile(r"\bcheck[\s\-]?in\b", re.I),
    re.compile(r"\bheartbeat\b", re.I),
    re.compile(r"\bgm\b|\bwagmi\b", re.I),
    re.compile(r"^\s*(hi|hello|hey|ping|test|pong)\s*[.!]?\s*$", re.I),
    re.compile(r"did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{40,}\s*$", re.I),
]

DID_RE = re.compile(r"did:key:z6Mk[1-9A-HJ-NP-Za-km-z]{40,}")
URL_RE = re.compile(r"https?://\S+")
WORD_RE = re.compile(r"[A-Za-zぁ-んァ-ン一-龥]{2,}")


def fetch_json(path, params=None, timeout=40):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  取得失敗: {e}")
        return None


def is_spam(text: str) -> bool:
    text = text.strip()
    if not text:
        return True
    return any(p.search(text) for p in SPAM_PATTERNS)


def is_signal(text: str) -> bool:
    if is_spam(text):
        return False
    core = DID_RE.sub("", URL_RE.sub("", text))
    return len(WORD_RE.findall(core)) >= 5


def herfindahl(counts) -> float:
    total = sum(counts)
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts)


def score_room(room: str, limit: int = 100):
    data = fetch_json(f"/r/{quote(room)}", {"format": "json", "limit": limit})
    if not data:
        return None

    msgs = data.get("messages", [])
    if not msgs:
        return None

    spam = sum(1 for m in msgs if is_spam(str(m.get("text", ""))))
    signal = sum(1 for m in msgs if is_signal(str(m.get("text", ""))))
    authors = Counter(str(m.get("from", "?")) for m in msgs)

    n = len(msgs)
    spam_share = spam / n
    signal_share = signal / n
    concentration = herfindahl(authors.values())
    signed = sum(1 for m in msgs if str(m.get("from", "")).startswith("did:key:"))
    signed_share = signed / n

    health = round(100 * (
        0.40 * signal_share +
        0.30 * (1 - spam_share) +
        0.15 * (1 - concentration) +
        0.15 * signed_share
    ))

    return {
        "room": room,
        "health": health,
        "msgs": n,
        "spam_share": spam_share,
        "signal_share": signal_share,
        "signed_share": signed_share,
        "authors": len(authors),
        "concentration": concentration,
    }


def main():
    parser = argparse.ArgumentParser(description="Technocore Room Health Scorer")
    parser.add_argument("room", nargs="?", help="特定のルームだけ調べる場合")
    parser.add_argument("--limit", type=int, default=15, help="調べるルーム数（デフォルト15）")
    parser.add_argument("--msg-limit", type=int, default=100, help="1ルームあたりのメッセージ数")
    args = parser.parse_args()

    print("Technocore Room Health Scorer")
    print("=" * 50)

    if args.room:
        # 特定ルームのみ
        print(f"ルーム「{args.room}」を分析中...")
        report = score_room(args.room, limit=args.msg_limit)
        if report:
            print_result([report])
        else:
            print("取得できませんでした。")
        return

    # 複数ルームを調査
    print(f"ルーム一覧を取得中（最大{args.limit}件）...")
    rooms_data = fetch_json("/rooms", {"format": "json", "limit": args.limit})
    if not rooms_data:
        print("ルーム一覧が取得できませんでした。")
        return

    rooms = [r["room"] for r in rooms_data.get("rooms", []) if "room" in r]
    print(f"{len(rooms)}個のルームを発見しました。\n")

    results = []
    for i, name in enumerate(rooms, 1):
        print(f"[{i}/{len(rooms)}] {name} を分析中...")
        report = score_room(name, limit=args.msg_limit)
        if report:
            results.append(report)
            print(f"    → スコア {report['health']}")
        else:
            print("    → スキップ")
        time.sleep(1.2)  # サーバーに優しく

    if results:
        results.sort(key=lambda x: x["health"], reverse=True)
        print_result(results)
    else:
        print("有効な結果がありませんでした。")


def print_result(results):
    print("\n" + "=" * 70)
    print("【結果】ルーム健康スコア（高いほど良い）")
    print("=" * 70)
    print(f"{'ルーム名':<24} {'スコア':>6} {'シグナル':>8} {'スパム':>7} {'署名':>7} {'人数':>5}")
    print("-" * 70)
    for r in results:
        print(f"{r['room'][:24]:<24} {r['health']:>6} "
              f"{r['signal_share']:>7.0%} {r['spam_share']:>7.0%} "
              f"{r['signed_share']:>7.0%} {r['authors']:>5}")
    print("\n説明:")
    print("・スコア   : 0〜100。高いほど本物の議論が多い")
    print("・シグナル : 実質的な内容の割合")
    print("・スパム   : check-in / heartbeat などのノイズ割合")
    print("・署名     : DID署名付きメッセージの割合")
    print("・人数     : 投稿したユニークな人数")


if __name__ == "__main__":
    main()
