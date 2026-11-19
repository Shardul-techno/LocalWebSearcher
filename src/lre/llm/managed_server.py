"""Lifecycle wrapper for a bundled llama-server executable on loopback only."""
import atexit
import socket
import subprocess
import time
import urllib.request
from pathlib import Path


class ManagedServer:
    def __init__(self, executable: Path, model: Path, log_dir: Path, context: int, threads: int, timeout_seconds: int = 45, command: list[str] | None = None):
        self.executable = executable
        self.model = model
        self.log_dir = log_dir
        self.context = context
        self.threads = threads
        self.timeout_seconds = timeout_seconds
        self.command = command
        self.process: subprocess.Popen | None = None
        self.port: int | None = None
        self._log = None
        atexit.register(self.stop)

    @property
    def base_url(self) -> str:
        if self.port is None:
            raise RuntimeError("Managed server has not started")
        return f"http://127.0.0.1:{self.port}/v1"

    def start(self) -> str:
        if self.process and self.process.poll() is None:
            return self.base_url
        if not self.executable.is_file() or not self.model.is_file():
            raise RuntimeError("Install a model and the bundled llama-server before research")
        self.port = _free_port()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log = (self.log_dir / "llama-server.log").open("ab")
        args = (self.command or [str(self.executable)]) + ["--model", str(self.model), "--host", "127.0.0.1", "--port", str(self.port), "--ctx-size", str(self.context), "--threads", str(self.threads)]
        self.process = subprocess.Popen(args, stdout=self._log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        deadline = time.monotonic() + self.timeout_seconds
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("llama-server exited; see logs/llama-server.log")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=1) as response:
                    if response.status < 500:
                        return self.base_url
            except OSError:
                time.sleep(0.2)
        self.stop()
        raise RuntimeError("llama-server did not become ready before its timeout")

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        if self._log:
            self._log.close()
            self._log = None


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
