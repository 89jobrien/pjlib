import unittest

from scripts.projects_extract import MessageEvent, ToolResultEvent, ToolUseEvent
from scripts.projects_log_parser import normalize_event


class TestProjectsLogParser(unittest.TestCase):
    def test_normalizes_message_event(self) -> None:
        ev = MessageEvent(
            session_id="S",
            uuid="u1",
            parent_uuid=None,
            timestamp="t1",
            role="user",
            text="hello",
        )
        row = normalize_event(ev)
        self.assertEqual(row["event_type"], "message")
        self.assertEqual(row["text"], "hello")
        self.assertEqual(row["tool_name"], None)

    def test_normalizes_tool_events(self) -> None:
        tu = ToolUseEvent(
            session_id="S",
            uuid="u2",
            parent_uuid=None,
            timestamp="t2",
            role="assistant",
            tool_name="Read",
            tool_use_id="toolu_1",
            tool_input={"path": "/tmp/x"},
        )
        tr = ToolResultEvent(
            session_id="S",
            uuid="u3",
            parent_uuid="u2",
            timestamp="t3",
            role="user",
            tool_use_id="toolu_1",
            is_error=False,
            content_text="ok",
        )
        tu_row = normalize_event(tu)
        tr_row = normalize_event(tr)
        self.assertEqual(tu_row["event_type"], "tool_use")
        self.assertEqual(tr_row["event_type"], "tool_result")
        self.assertEqual(tr_row["tool_result_text"], "ok")


if __name__ == "__main__":
    unittest.main()
