import logging
import azure.functions as func
import pyodbc
import os
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # クエリパラメータから 'id' を取得
    id = req.params.get('id')

    # あるとテストの動作が不安定になる！？
    if not id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            id = req_body.get('id')

    # 'id' が指定されていない場合はエラーレスポンスを返す
    if not id:
        return func.HttpResponse(
            json.dumps({"error": "パラメータ 'id' が必要です"}),
            mimetype="application/json",
            status_code=400
        )

    # idが指定されている場合はデータベースから情報を取得する
    try:
        # 環境変数から接続文字列を取得
        with pyodbc.connect(os.environ['CONNECTION_STRING']) as connection:
            # データベース接続を開く
            with connection.cursor() as cursor:
                # パラメータ化クエリを使用してSQLインジェクションを防止
                cursor.execute('SELECT name FROM D0192 WHERE id = ?', (id,))
                row = cursor.fetchone()

                # データが見つからない場合はエラーレスポンスを返す
                if not row:
                    return func.HttpResponse(
                        json.dumps({"error": "指定されたIDのデータが見つかりません"}),
                        mimetype="application/json",
                        status_code=404
                    )

                # データが見つかった場合はJSONレスポンスを返す
                return func.HttpResponse(
                    json.dumps({"id": id, "name": row[0]}),
                    mimetype="application/json",
                    status_code=200
                )

    # データベース接続エラーをキャッチして適切なレスポンスを返す
    except pyodbc.Error as e:
        logging.error(f"Database error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "データベースエラーが発生しました"}),
            mimetype="application/json",
            status_code=500
        )
    
    # その他の予期しないエラーをキャッチして適切なレスポンスを返す
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "予期せぬエラーが発生しました"}),
            mimetype="application/json",
            status_code=500
        )