"""M6 smoke checks. Skipped when Tcl/Tk or a display is unavailable."""

from unittest.mock import MagicMock

import pytest

tk = pytest.importorskip("tkinter")

from lre.ui.tk_app import ResearchWindow


def test_research_window_builds_and_reports_missing_model():
    service = MagicMock()
    service.model_ready.return_value = (False, "No managed model is selected")
    service.projects.return_value = ["inbox"]
    service.history.return_value = []
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.withdraw()
    try:
        window = ResearchWindow(root, service)
        assert "No local model ready" in window.progress.get()
        assert window.run_button.instate(["!disabled"])\n        assert window.prompt_entry.bind("<Return>")
    finally:
        root.destroy()
