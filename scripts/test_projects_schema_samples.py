import json
import tempfile
import unittest
from pathlib import Path

from scripts.projects_schema_samples import extract_schema_samples


class TestProjectsSchemaSamples(unittest.TestCase):
    def test_extracts_schema_samples_by_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.jsonl"
            rows = [
                {"type": "assistant", "message": {"role": "assistant", "content": "hi"}},
                {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": [{"type": "text", "text": "yo"}],
                    },
                    "extra": 123,
                },
            ]
            path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

            samples = extract_schema_samples([path], sample_limit=2)
            self.assertEqual(samples["total_records"], 2)
            self.assertEqual(samples["types"]["assistant"]["count"], 1)
            self.assertEqual(samples["types"]["user"]["count"], 1)

            user_schema = samples["types"]["user"]["schema"]
            self.assertIn("message", user_schema["properties"])
            self.assertIn("object", user_schema["properties"]["message"]["type"])


if __name__ == "__main__":
    unittest.main()
