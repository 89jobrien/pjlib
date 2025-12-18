import unittest

from scripts.projects_dataset import iter_dataset_rows_from_events
from scripts.projects_extract import MessageEvent, ToolResultEvent, ToolUseEvent


class TestProjectsDataset(unittest.TestCase):
    def test_pairs_tool_use_with_tool_result(self) -> None:
        events = [
            MessageEvent(
                session_id="S",
                uuid="m1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                text="do it",
            ),
            ToolUseEvent(
                session_id="S",
                uuid="a1",
                parent_uuid="m1",
                timestamp="t2",
                role="assistant",
                tool_name="Read",
                tool_use_id="toolu_1",
                tool_input={"path": "/tmp/x"},
            ),
            ToolResultEvent(
                session_id="S",
                uuid="u1",
                parent_uuid="a1",
                timestamp="t3",
                role="user",
                tool_use_id="toolu_1",
                is_error=False,
                content_text="ok",
            ),
        ]

        rows = list(iter_dataset_rows_from_events(events, max_context_messages=10))
        self.assertEqual(len(rows), 1)
        r = rows[0]

        self.assertEqual(r["session_id"], "S")
        self.assertEqual(r["tool_name"], "Read")
        self.assertEqual(r["tool_input"], {"path": "/tmp/x"})
        self.assertEqual(r["tool_result"]["is_error"], False)
        self.assertEqual(r["tool_result"]["content_text"], "ok")
        self.assertEqual(r["reward"], 1.0)

        # context messages captured at tool_use
        self.assertEqual(len(r["messages"]), 1)
        self.assertEqual(r["messages"][0]["text"], "do it")

        # trace has tool_use then tool_result
        self.assertEqual([t["type"] for t in r["trace"]], ["tool_use", "tool_result"])

    def test_trace_includes_intermediate_messages_by_default(self) -> None:
        events = [
            ToolUseEvent(
                session_id="S",
                uuid="a1",
                parent_uuid=None,
                timestamp="t2",
                role="assistant",
                tool_name="Read",
                tool_use_id="toolu_1",
                tool_input={"path": "/tmp/x"},
            ),
            MessageEvent(
                session_id="S",
                uuid="m2",
                parent_uuid="a1",
                timestamp="t2.5",
                role="assistant",
                text="working...",
            ),
            ToolResultEvent(
                session_id="S",
                uuid="u1",
                parent_uuid="a1",
                timestamp="t3",
                role="user",
                tool_use_id="toolu_1",
                is_error=False,
                content_text="ok",
            ),
        ]

        rows = list(iter_dataset_rows_from_events(events, max_context_messages=10))
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            [t["type"] for t in rows[0]["trace"]],
            ["tool_use", "message", "tool_result"],
        )

    def test_reward_is_negative_on_error(self) -> None:
        events = [
            ToolUseEvent(
                session_id="S",
                uuid="a1",
                parent_uuid=None,
                timestamp="t2",
                role="assistant",
                tool_name="Bash",
                tool_use_id="toolu_2",
                tool_input={"command": "false"},
            ),
            ToolResultEvent(
                session_id="S",
                uuid="u1",
                parent_uuid="a1",
                timestamp="t3",
                role="user",
                tool_use_id="toolu_2",
                is_error=True,
                content_text="boom",
            ),
        ]

        rows = list(iter_dataset_rows_from_events(events))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reward"], -1.0)


if __name__ == "__main__":
    unittest.main()
