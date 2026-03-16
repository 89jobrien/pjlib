#!/usr/bin/env python3
"""
Detect emojis in text files and generate a report.
Usage: python detect_emojis.py <directory> [--json]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

# Unicode emoji ranges
EMOJI_PATTERN = re.compile(
    "["
    "\U0001f300-\U0001f9ff"  # Emoticons, symbols, pictographs
    "\U00002600-\U000026ff"  # Miscellaneous symbols
    "\U00002700-\U000027bf"  # Dingbats
    "\U0001f000-\U0001f02f"  # Mahjong tiles
    "\U0001f0a0-\U0001f0ff"  # Playing cards
    "\U0001f100-\U0001f64f"  # Enclosed characters
    "\U0001f680-\U0001f6ff"  # Transport and map symbols
    "✅❌☑✓☐⚠️📝💡🐛🚀🔴🟡🟢"  # Common status emojis
    "]+",
    flags=re.UNICODE,
)


def find_emojis_in_file(filepath: Path) -> List[Dict]:
    """Find all emojis in a file with line numbers and context."""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                matches = EMOJI_PATTERN.finditer(line)
                for match in matches:
                    # Get context (40 chars before and after)
                    start = max(0, match.start() - 40)
                    end = min(len(line), match.end() + 40)
                    context = line[start:end].strip()

                    results.append(
                        {
                            "line": line_num,
                            "emoji": match.group(),
                            "context": context,
                            "full_line": line.strip(),
                        }
                    )
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return results


def scan_directory(directory: Path, extensions: List[str]) -> Dict:
    """Scan directory for files containing emojis."""
    results = {}

    for ext in extensions:
        for filepath in directory.rglob(f"*{ext}"):
            # Skip hidden files and directories
            if any(part.startswith(".") for part in filepath.parts):
                continue

            emojis = find_emojis_in_file(filepath)
            if emojis:
                results[str(filepath.relative_to(directory))] = emojis

    return results


def generate_report(results: Dict, json_output: bool = False) -> str:
    """Generate human-readable or JSON report."""
    if json_output:
        summary = {
            "total_files": len(results),
            "total_emojis": sum(len(emojis) for emojis in results.values()),
            "files": results,
        }
        return json.dumps(summary, indent=2)

    # Human-readable report
    total_emojis = sum(len(emojis) for emojis in results.values())

    report = ["# Emoji Detection Report\n"]
    report.append(f"**Files with emojis:** {len(results)}")
    report.append(f"**Total emojis found:** {total_emojis}\n")

    if not results:
        report.append("No emojis found!")
        return "\n".join(report)

    report.append("## Files\n")

    for filepath, emojis in sorted(
        results.items(), key=lambda x: len(x[1]), reverse=True
    ):
        report.append(f"### {filepath} ({len(emojis)} emojis)\n")

        # Show first 5 occurrences
        for emoji_data in emojis[:5]:
            report.append(
                f"- Line {emoji_data['line']}: `{emoji_data['emoji']}` "
                f'in "{emoji_data["context"]}"'
            )

        if len(emojis) > 5:
            report.append(f"  ... and {len(emojis) - 5} more\n")
        else:
            report.append("")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Detect emojis in text files")
    parser.add_argument("directory", type=Path, help="Directory to scan")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".md", ".txt"],
        help="File extensions to scan (default: .md .txt)",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory {args.directory} does not exist", file=sys.stderr)
        sys.exit(1)

    results = scan_directory(args.directory, args.extensions)
    report = generate_report(results, args.json)
    print(report)


if __name__ == "__main__":
    main()
