# x-garage-D0701-2025Training-Functions

## 1．機能要件と仕様

- Azure Functions (Python) によるHTTPトリガーAPIを提供する。
- クエリパラメータまたはリクエストボディで `id` を受け取り、SQL Server（ODBC経由）から該当データ（name）を取得しJSONで返却する。
- `id` が未指定・不正・該当データなし・DBエラー等の場合は適切なエラーレスポンスを返す。

## 2．プログラム構成
2. 環境変数 `CONNECTION_STRING` にDB接続文字列を設定
3. Azure Functions Core Toolsで起動

## 3．関数一覧と仕様

- [`function_app.http_trigger`](function_app.py)
  - HTTPリクエストを受け付け、`id` を元にDB検索し結果をJSONで返す。
  - エラー時は適切なHTTPステータス・エラーメッセージを返す。

- `DummyRequest`（テスト用クラス）  
  - テスト時にリクエストのモックとして使用。

- テスト関数（`test/test_func.py`）
  - 各種正常系・異常系の動作検証。

## 4．利用方法

1. 必要なパッケージをインストール
2. API呼び出し例

## 5．備考

- DBテーブル名やカラム名は `D0701(id, name)` を想定。
- テストは `pytest` で実行可能（`python -m pytest`）。
- Azure Functionsの認証レベルは `FUNCTION` です。
- 詳細なエラー内容はログにのみ出力されます。
