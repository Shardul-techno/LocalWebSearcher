import sys
from pathlib import Path

import pytest

from lre.llm.managed_server import ManagedServer


@pytest.mark.integration
def test_managed_server_starts_and_stops_fake_server(tmp_path: Path):
    script = tmp_path / "fake_server.py"
    script.write_text('''import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--port", type=int, required=True)
args, _ = parser.parse_known_args()
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *_): pass
HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
''', encoding="utf-8")
    model = tmp_path / "model.gguf"
    model.write_bytes(b"test")
    server = ManagedServer(script, model, tmp_path / "logs", 128, 1, timeout_seconds=5, command=[sys.executable, str(script)])
    assert server.start().startswith("http://127.0.0.1:")
    assert server.process and server.process.poll() is None
    server.stop()
    assert server.process is None
