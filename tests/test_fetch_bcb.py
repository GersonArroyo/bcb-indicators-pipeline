import json
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.adapters import HTTPAdapter
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from scripts.fetch_bcb import create_retry_session, json_downloader


class RetryTestHandler(BaseHTTPRequestHandler):
    request_count = 0

    def do_GET(self):
        RetryTestHandler.request_count += 1

        if RetryTestHandler.request_count < 3:
            self.send_response(503)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, format, *args):
        pass
    
    
def test_retry_session_retries_transient_http_errors():
    RetryTestHandler.request_count = 0

    server = HTTPServer(("127.0.0.1", 0), RetryTestHandler)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )
    thread.start()

    try:
        session = create_retry_session()

        retry_adapter = session.get_adapter("https://")
        session.mount("http://", retry_adapter)

        host = "127.0.0.1"
        port = server.server_port

        response = session.get(
            f"http://{host}:{port}/",
            timeout=(1, 1)
        )

        assert response.status_code == 200
        assert RetryTestHandler.request_count == 3

    finally:
        server.shutdown()
        server.server_close()


def test_create_retry_session_configures_retry_policy():
    session = create_retry_session()

    adapter = session.get_adapter("https://")
    
    assert isinstance(adapter, HTTPAdapter)
    
    retry = adapter.max_retries

    assert retry.total == 2
    assert retry.backoff_factor == 1
    assert set(retry.status_forcelist) == {408, 429, 500, 502, 503, 504}
    
    assert retry.allowed_methods is not None
    assert set(retry.allowed_methods) == {"GET"}
    
    
def test_json_downloader_propagates_request_error(tmp_path):
    series_path = tmp_path / "series.json"

    series_path.write_text(
        json.dumps([
            {
                "series_code": 1,
                "frequency": "daily"
            }
        ])
    )

    mock_session = MagicMock()
    mock_session.get.side_effect = requests.exceptions.ReadTimeout(
        "API timeout"
    )

    with patch(
        "scripts.fetch_bcb.create_retry_session",
        return_value=mock_session
    ):
        with pytest.raises(requests.exceptions.ReadTimeout):
            json_downloader(
                series_path=series_path,
                url="https://example.com/",
                output_path=tmp_path / "raw",
                end_date="2026-10-25"
            )