import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class HookPayload:
    event: str
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    context: dict[str, str] | None = None
    timestamp: str | None = None


@dataclass
class HookResponse:
    allow: bool
    reason: str | None = None
    system_message: str | None = None
    updated_input: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> str:
        # Remove None values
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


def list_hook_scripts() -> list[Path]:
    hooks_root = Path(__file__).parent
    scripts: list[Path] = []
    include_dirs = {
        hooks_root / "analyzers",
        hooks_root / "context",
        hooks_root / "guards",
        hooks_root / "lifecycle",
        hooks_root / "workflows",
    }
    for directory in include_dirs:
        for path in directory.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            if path.name.startswith("test_"):
                continue
            scripts.append(path)
    for path in hooks_root.glob("*.py"):
        if path.name in {"claude_hooks.py", "hook_logging.py", "test_hook_logging.py"}:
            continue
        if path.name.startswith("test_"):
            continue
        scripts.append(path)
    return sorted(set(scripts))


def run(handler):
    """
    Standard entry point for hooks.
    Reads payload from stdin, calls handler, and writes response to stdout.
    """
    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            return

        data = json.loads(raw_input)
        payload = HookPayload(**data)

        response = handler(payload)

        if isinstance(response, HookResponse):
            print(response.to_json())
        else:
            print(json.dumps(response))

    except Exception as e:
        print(f"Error in hook: {e}", file=sys.stderr)
        print(json.dumps({"allow": True}))
