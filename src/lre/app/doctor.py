from typing import Any

from lre.llm.registry import build_backend


def check_model(profile: dict[str, Any]) -> tuple[bool, str]:
    checker = getattr(build_backend(profile), "doctor", None)
    if checker is None:
        return False, "This backend does not provide a doctor check."
    return checker()
