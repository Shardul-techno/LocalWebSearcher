from collections import deque


class FakeBackend:
    def __init__(self, responses: list[str]):
        self.responses = deque(responses)

    def generate(self, prompt: str, schema: dict | None = None) -> str:
        if not self.responses:
            raise RuntimeError("Fake backend has no scripted response")
        return self.responses.popleft()
