import unittest

from scripts.pj_extract import (
    MessageEvent,
    ToolResultEvent,
    ToolUseEvent,
    extract_events,
)


class TestProjectsExtract(unittest.TestCase):
    def test_extracts_tool_use(self) -> None:
        rec = {
            "type": "assistant",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_123",
                        "name": "Read",
                        "input": {"path": "/tmp/x"},
                    }
                ],
            },
        }
        evs = extract_events(rec)
        tus = [e for e in evs if isinstance(e, ToolUseEvent)]
        self.assertEqual(len(tus), 1)
        self.assertEqual(tus[0].tool_name, "Read")
        self.assertEqual(tus[0].tool_use_id, "toolu_123")
        self.assertEqual(tus[0].tool_input, {"path": "/tmp/x"})

    def test_extracts_tool_result(self) -> None:
        rec = {
            "type": "user",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_123",
                        "is_error": True,
                        "content": [{"type": "text", "text": "boom"}],
                    }
                ],
            },
        }
        evs = extract_events(rec)
        trs = [e for e in evs if isinstance(e, ToolResultEvent)]
        self.assertEqual(len(trs), 1)
        self.assertTrue(trs[0].is_error)
        self.assertEqual(trs[0].tool_use_id, "toolu_123")
        self.assertEqual(trs[0].content_text, "boom")

    def test_extracts_plain_text_message(self) -> None:
        rec = {
            "type": "user",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {"role": "user", "content": "hello"},
        }
        evs = extract_events(rec)
        msgs = [e for e in evs if isinstance(e, MessageEvent)]
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].text, "hello")


if __name__ == "__main__":
    unittest.main()
