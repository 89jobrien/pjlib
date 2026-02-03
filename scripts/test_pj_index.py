import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

from scripts.pj_index import DEFAULT_BUCKETS, build_pj_index


class TestProjectsIndex(unittest.TestCase):
    def test_builds_bucket_counts_and_top_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sizes = [100, 2 * 1024 * 1024, 10 * 1024 * 1024]
            for idx, size in enumerate(sizes):
                path = root / f"file_{idx}.jsonl"
                path.write_bytes(b"a" * size)

            index = cast(dict[str, Any], build_pj_index(root, top_n=2))

            self.assertEqual(index["summary"]["total_files"], 3)
            self.assertEqual(index["summary"]["total_bytes"], sum(sizes))
            self.assertEqual(len(index["top_files"]), 2)
            self.assertEqual(index["top_files"][0]["size_bytes"], max(sizes))

            buckets = cast(list[dict[str, Any]], index["buckets"])
            bucket_counts = {b["bucket"]: b["count"] for b in buckets}
            for size in sizes:
                label = _bucket_label_for_size(size)
                self.assertGreater(bucket_counts[label], 0)


def _bucket_label_for_size(size: int) -> str:
    for label, low, high in DEFAULT_BUCKETS:
        if low <= size < high:
            return label
    return DEFAULT_BUCKETS[-1][0]


if __name__ == "__main__":
    unittest.main()
