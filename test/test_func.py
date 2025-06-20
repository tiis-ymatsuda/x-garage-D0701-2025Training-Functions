import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import function_app

# filepath: c:\Users\D0701\Desktop\functionstest\test\test_func.py

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class DummyRequest:
    def __init__(self, params=None, json_body=None):
        self.params = params or {}
        self._json_body = json_body

    def get_json(self):
        if self._json_body is None:
            raise ValueError
        return self._json_body

@patch('function_app.pyodbc.connect')
def test_http_trigger_success(mock_connect):
    req = DummyRequest(params={'id': '1'})
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ('TestName',)
    mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    resp = function_app.http_trigger(req)
    assert resp.status_code == 200
    assert '"id": "1"' in resp.get_body().decode()
    assert '"name": "TestName"' in resp.get_body().decode()

@patch('function_app.pyodbc.connect')
def test_http_trigger_not_found(mock_connect):
    req = DummyRequest(params={'id': '2'})
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

    resp = function_app.http_trigger(req)
    assert resp.status_code == 404
    assert "データが見つかりません" in resp.get_body().decode()

def test_http_trigger_missing_id():
    req = DummyRequest()
    resp = function_app.http_trigger(req)
    assert resp.status_code == 400
    assert "パラメータ" in resp.get_body().decode()

def test_http_trigger_invalid_id():
    req = DummyRequest(params={'id': 'abc'})
    resp = function_app.http_trigger(req)
    assert resp.status_code == 400
    assert "パラメータ" in resp.get_body().decode()

@patch.dict(os.environ, {}, clear=True)
def test_http_trigger_missing_connection_string():
    req = DummyRequest(params={'id': '1'})
    resp = function_app.http_trigger(req)
    assert resp.status_code == 500
    assert "サーバー設定エラー" in resp.get_body().decode()

@patch('function_app.pyodbc.connect', side_effect=Exception("unexpected"))
def test_http_trigger_unexpected_error(mock_connect):
    req = DummyRequest(params={'id': '1'})
    resp = function_app.http_trigger(req)
    assert resp.status_code == 500
    assert "予期せぬエラー" in resp.get_body().decode()

@patch('function_app.pyodbc.connect', side_effect=function_app.pyodbc.Error("db error"))
def test_http_trigger_db_error(mock_connect):
    req = DummyRequest(params={'id': '1'})
    resp = function_app.http_trigger(req)
    assert resp.status_code == 500
    assert "データベースエラー" in resp.get_body().decode()

def test_http_trigger_id_in_body():
    req = DummyRequest(json_body={'id': '3'})
    with patch('function_app.pyodbc.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('BodyName',)
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        resp = function_app.http_trigger(req)
        assert resp.status_code == 200
        assert '"id": "3"' in resp.get_body().decode()
        assert '"name": "BodyName"' in resp.get_body().decode()

def test_http_trigger_id_zero():
    req = DummyRequest(params={'id': '0'})
    with patch('function_app.pyodbc.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('ZeroName',)
        mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        resp = function_app.http_trigger(req)
        assert resp.status_code == 200
        assert '"id": "0"' in resp.get_body().decode()
        assert '"name": "ZeroName"' in resp.get_body().decode()

def test_http_trigger_body_value_error():
    req = DummyRequest()
    # get_json will raise ValueError
    resp = function_app.http_trigger(req)
    assert resp.status_code == 400
    assert "パラメータ" in resp.get_body().decode()