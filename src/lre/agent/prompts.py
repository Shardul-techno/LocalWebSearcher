from pathlib import Path


class PromptLibrary:
    def __init__(self, prompt_dir: Path):
        self.prompt_dir = prompt_dir

    def render(self, name: str, **values: object) -> str:
        template = (self.prompt_dir / f"{name}.txt").read_text(encoding="utf-8")
        return template.format(**values)
