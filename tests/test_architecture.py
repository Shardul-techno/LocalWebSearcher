import ast
from pathlib import Path


def test_core_imports_nothing_from_lre_and_ui_uses_only_facade_and_core():
    root = Path(__file__).parents[1] / "src" / "lre"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
        rel = path.relative_to(root).parts
        if rel[0] == "core":
            assert not any(name == "lre" or name.startswith("lre.") for name in imports)
        if rel[0] == "ui":
            forbidden = ("lre.llm", "lre.search", "lre.fetch", "lre.agent", "lre.storage")
            assert not any(name.startswith(forbidden) for name in imports)
