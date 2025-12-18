"""Compatibility shim.

New canonical location: `hooks/hook_logging.py`.
Old import path kept working: `from utils.hook_logging import hook_invocation`.
"""

from __future__ import annotations

from hook_logging import HookInvocation, hook_invocation

__all__ = ["HookInvocation", "hook_invocation"]
