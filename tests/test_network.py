import json

import httpx

from lre.fetch.network import request_with_retry, sanitized_url


def test_sanitized_url_drops_query_parameters():
    assert sanitized_url("https://example.org/page?token=secret") == "https://example.org/page"


def test_retryable_http_status_retries_and_logs(tmp_path):
    calls = {"count": 0}
    def handler(request):
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(503, request=request, text="temporary")
        return httpx.Response(200, request=request, text="ok")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = request_with_retry(client, "GET", "https://example.org/page?key=secret",
                                      log_dir=tmp_path, max_retries=1)
        try:
            assert response.status_code == 200
        finally:
            response.close()
    assert calls["count"] == 2
    log = (tmp_path / "network-errors.jsonl").read_text(encoding="utf-8")
    assert "secret" not in log
    record = json.loads(log.splitlines()[0])
    assert record["http_status"] == 503
    assert record["retryable"] is True


def test_permanent_http_status_is_not_retried(tmp_path):
    calls = {"count": 0}
    def handler(request):
        calls["count"] += 1
        return httpx.Response(404, request=request)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = request_with_retry(client, "GET", "https://example.org/missing",
                                      log_dir=tmp_path, max_retries=3)
        try:
            assert response.status_code == 404
        finally:
            response.close()
    assert calls["count"] == 1


def test_transient_connection_error_retries(tmp_path):
    calls = {"count": 0}
    def handler(request):
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ConnectError("connection reset", request=request)
        return httpx.Response(200, request=request)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = request_with_retry(client, "GET", "https://example.org",
                                      log_dir=tmp_path, max_retries=1)
        try:
            assert response.status_code == 200
        finally:
            response.close()
    assert calls["count"] == 2
