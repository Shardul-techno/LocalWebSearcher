import re


def clean(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def parse_queries(text: str, limit: int) -> list[str]:
    try:
        lines = [re.sub(r"^\s*(?:[-*\d.)]+\s*)", "", line).strip(" \t\"'") for line in clean(text).splitlines()]
        return [line for line in lines if line][:max(0, limit)]
    except Exception:
        return []


def parse_ids(text: str) -> list[int]:
    try:
        value = clean(text)
        if re.search(r"\bNONE\b", value, re.IGNORECASE):
            return []
        match = re.search(r"IDS\s*:\s*([^\n]+)", value, re.IGNORECASE)
        return [int(item) for item in re.findall(r"\d+", match.group(1) if match else value)]
    except Exception:
        return []


def parse_judgment(text: str) -> tuple[bool, str]:
    value = clean(text)
    sufficient = bool(re.search(r"\bSUFFICIENT\b", value, re.IGNORECASE)) and not bool(re.search(r"\bINSUFFICIENT\b", value, re.IGNORECASE))
    gap = re.search(r"GAP\s*:\s*(.+)", value, re.IGNORECASE)
    return sufficient, gap.group(1).strip() if gap else ""
