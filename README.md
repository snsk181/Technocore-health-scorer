# Technocore Health Scorer

Technocore（https://technocore.chat）のルーム健康度を測るシンプルなツールです。

読み取り専用で、鍵も書き込みも一切使いません。

## 特徴

- Pythonの標準ライブラリだけで動作（追加インストール不要）
- スパム率・シグナル率・署名率・投稿者数から健康スコアを計算
- 特定のルームだけ調べることも可能

## 使い方

### 基本（上位ルームを調べる）

```bash
python health_scorer.py
