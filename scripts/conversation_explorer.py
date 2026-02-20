#!/usr/bin/env python3
"""Conversation Explorer CLI - Standalone script."""

import sys
from pathlib import Path

# Add parent directory to path to import conversation_explorer
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_explorer.cli import cli

if __name__ == "__main__":
    cli()
