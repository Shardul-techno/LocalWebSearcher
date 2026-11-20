"""Shared HTTP retry policy and privacy-safe network diagnostics."""
import json
import random
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import httpx

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


def sanitized_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.hostname or ""
    if parts.port:
        host += f":{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def log_error(log_dir: Path | None, operation: str, url: str, error: BaseException | str,
              status: int | None, timeout: object, attempt: int, retryable: bool) -> None:
    if log_dir is None:
        return
    cause = getattr(error, "__cause__", None)
    message = re.sub(r"(https?://[^?\s]+)\?[^\s]+", r"\1?<redacted>", str(error))[:1000]
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "url": sanitized_url(url),
        "error_type": type(error).__name__ if isinstance(error, BaseException) else "HTTPStatusError",
        "message": message,
        "http_status": status,
        "os_error_code": getattr(error, "errno", None) or getattr(cause, "errno", None),
        "timeout": str(timeout) if timeout is not None else None,
        "retry_count": attempt,
        "retryable": retryable,
    }
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "network-errors.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return min(max(float(value), 0), 10)
    except ValueError:
        try:
            seconds = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            return min(max(seconds, 0), 10)
        except (TypeError, ValueError, OverflowError):
            return None


def request_with_retry(client: httpx.Client, method: str, url: str, *, log_dir: Path | None = None,
                       operation: str = "http_request", max_retries: int = 2, **kwargs) -> httpx.Response:
    timeout = kwargs.get("timeout", client.timeout)
    for attempt in range(max_retries + 1):
        try:
            request = client.build_request(method, url, **kwargs)
            response = client.send(request, stream=True)
            if response.status_code in RETRYABLE_STATUS:
                log_error(log_dir, operation, url, f"HTTP {response.status_code}", response.status_code,
                          timeout, attempt, attempt < max_retries)
                if attempt < max_retries:
                    delay = _retry_after(response)
                    response.close()
                    time.sleep(delay if delay is not None else min(0.25 * (2 ** attempt) + random.uniform(0, .1), 5))
                    continue
            elif response.status_code >= 400:
                log_error(log_dir, operation, url, f"HTTP {response.status_code}", response.status_code,
                          timeout, attempt, False)
            return response
        except httpx.HTTPError as exc:
            current = exc
            certificate_error = False
            while current is not None:
                if "CERTIFICATE_VERIFY_FAILED" in str(current).upper():
                    certificate_error = True
                    break
                current = current.__cause__
            transient = isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)) and not certificate_error
            log_error(log_dir, operation, url, exc, None, timeout, attempt, transient and attempt < max_retries)
            if not transient or attempt >= max_retries:
                raise
            time.sleep(min(0.25 * (2 ** attempt) + random.uniform(0, .1), 5))
    raise RuntimeError("HTTP retry loop exited unexpectedly")
