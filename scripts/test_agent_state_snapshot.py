import unittest

from scripts.agent_state_snapshot import extract_shell_snapshot_state


class TestExtractShellSnapshotState(unittest.TestCase):
    def test_extracts_functions_aliases_exports(self) -> None:
        text = """# Snapshot file
# comment: foo () { not a function }
unalias -a 2>/dev/null || true
foo () {
  echo hi
}
bar(){ :; }
function baz { :; }
alias ll='ls -la'
typeset -x PATH=/bin:/usr/bin
export HOME=/Users/joe
setopt NO_shwordsplit
"""

        st = extract_shell_snapshot_state(text, max_names=500)

        self.assertEqual(st["kind"], "shell_snapshot_v1")
        self.assertGreater(st["bytes"], 0)
        self.assertGreater(st["line_count"], 0)

        self.assertEqual(st["function_count"], 3)
        self.assertEqual(st["alias_count"], 1)
        self.assertEqual(st["export_count"], 2)
        self.assertEqual(st["setopt_line_count"], 1)

        self.assertEqual(st["function_names"], ["bar", "baz", "foo"])
        self.assertEqual(st["alias_names"], ["ll"])
        self.assertEqual(st["export_names"], ["HOME", "PATH"])

        # hashed lists line up with capped name lists
        self.assertEqual(len(st["function_name_hashes"]), len(st["function_names"]))
        self.assertEqual(len(st["alias_name_hashes"]), len(st["alias_names"]))
        self.assertEqual(len(st["export_name_hashes"]), len(st["export_names"]))

    def test_is_deterministic(self) -> None:
        text = "foo () { :; }\nexport X=1\n"
        a = extract_shell_snapshot_state(text)
        b = extract_shell_snapshot_state(text)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
