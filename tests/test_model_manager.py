import hashlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from lre.llm.model_manager import ModelError, ModelManager


class DownloadServer:
    def __init__(self, body: bytes):
        self.body = body
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                start = int(self.headers.get("Range", "bytes=0-").split("=")[1].split("-")[0])
                self.send_response(206 if "Range" in self.headers else 200)
                self.send_header("Content-Length", str(len(outer.body) - start))
                self.end_headers()
                self.wfile.write(outer.body[start:])
            def log_message(self, *_args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_port}/model.gguf"

    def __exit__(self, *_args):
        self.server.shutdown()


def make_catalog(path: Path, url: str, digest: str = "") -> None:
    path.write_text(f'''[[models]]
id = "small"
name = "Small"
url = "{url}"
sha256 = "{digest}"
size_bytes = 16
context = 128
min_ram_mb = 1
license = "test"
platforms = ["windows"]
recommended = true
''', encoding="utf-8")


@pytest.mark.integration
def test_download_resumes_and_records_confirmed_hash(tmp_path: Path):
    body = b"0123456789abcdef"
    with DownloadServer(body) as url:
        catalog = tmp_path / "catalog.toml"
        make_catalog(catalog, url, hashlib.sha256(body).hexdigest())
        manager = ModelManager(tmp_path / "models", catalog)
        partial = tmp_path / "models" / "small.gguf.part"
        partial.parent.mkdir()
        partial.write_bytes(body[:4])
        result = manager.install("small")
    assert result.read_bytes() == body
    assert manager.active_path() is None
    assert manager.set_active("small") == result


@pytest.mark.integration
def test_hash_mismatch_removes_partial(tmp_path: Path):
    with DownloadServer(b"content") as url:
        catalog = tmp_path / "catalog.toml"
        make_catalog(catalog, url, "0" * 64)
        manager = ModelManager(tmp_path / "models", catalog)
        with pytest.raises(ModelError, match="hash"):
            manager.install("small")
    assert not (tmp_path / "models" / "small.gguf.part").exists()


@pytest.mark.integration
def test_cancel_keeps_partial_for_later_resume(tmp_path: Path):
    with DownloadServer(b"content") as url:
        catalog = tmp_path / "catalog.toml"
        make_catalog(catalog, url)
        manager = ModelManager(tmp_path / "models", catalog)
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(ModelError, match="cancelled"):
            manager.install("small", cancel=cancel)
    assert (tmp_path / "models" / "small.gguf.part").exists()
