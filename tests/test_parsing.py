from lre.agent.parsing import parse_ids, parse_judgment, parse_queries
from lre.llm.fake import FakeBackend


def test_parse_ids_tolerates_chatter_and_think_blocks():
    assert parse_ids("<think>ignore 99</think> Here you go\nIDS: 3, 7, 7, x") == [3, 7, 7]


def test_parse_bad_and_none_ids():
    assert parse_ids("garbled") == []
    assert parse_ids("IDS: NONE") == []


def test_parse_plan_and_judgment():
    assert parse_queries("1. first query\n- second query", 1) == ["first query"]
    assert parse_judgment("VERDICT: INSUFFICIENT | GAP: date") == (False, "date")
    assert parse_judgment("VERDICT: SUFFICIENT") == (True, "")


def test_fake_backend_is_scripted():
    backend = FakeBackend(["ok"])
    assert backend.generate("prompt") == "ok"
