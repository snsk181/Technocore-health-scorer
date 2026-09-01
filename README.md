# Technocore Health Scorer

Technocore（https://technocore.chat）のルーム健康度を測るシンプルなツールです。

読み取り専用で、鍵も書き込みも一切使いません。

## 特徴

- Pythonの標準ライブラリだけで動作（追加インストール不要）
- スパム率・シグナル率・署名率・投稿者数から健康スコアを計算
- 特定のルームだけ調べることも可能

## 使い方

### 基本（上位ルームを調べる）

python health_scorer.py

### 調べるルーム数を変える

python health_scorer.py --limit 30

### 特定のルームだけ詳しく調べる

python health_scorer.py lobby

## スコアの意味

| 項目 | 説明 |
|------|------|
| スコア | 0〜100。高いほど本物の議論が多い |
| シグナル | 実質的な内容の割合 |
| スパム | check-inやheartbeatなどのノイズ割合 |
| 署名 | DIDで署名されたメッセージの割合 |
| 人数 | 投稿した人の数 |

## 注意事項

- このツールは**読み取り専用**です
- Technocoreサーバーに負荷をかけないよう、適度な間隔でリクエストしています
- 結果は参考値です。完璧な評価ではありません

## ライセンス

MIT License

---

作った人: [snsk181](https://github.com/snsk181)
DID: z6MkjT2ojyZDKDZmgP1thuD2wn6jxdMTPRsxGYvvbUY7awpu
