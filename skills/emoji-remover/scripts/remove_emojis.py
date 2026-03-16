#!/usr/bin/env python3
"""
Remove and replace emojis in text files with text equivalents.
Usage: python remove_emojis.py <directory> [--apply] [--dry-run]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Emoji replacement mappings
STATUS_REPLACEMENTS = {
    '✅': '[DONE]',
    '❌': '[FAILED]',
    '🔴': 'CRITICAL:',
    '🟡': 'MEDIUM:',
    '🟢': 'LOW:',
    '⚠️': 'WARNING:',
    '📝': 'NOTE:',
    '💡': 'TIP:',
    '🐛': 'BUG:',
    '🚀': 'FEATURE:',
    '☑': '[x]',
    '✓': '[x]',
    '☐': '[ ]',
    '📁': 'Directory:',
    '📄': 'File:',
    '🔧': 'Config:',
    '🤖': 'AI:',
}

# Decorative emojis to remove entirely
DECORATIVE_EMOJIS = re.compile(
    r'[🎉🎊💪👍🔥✨🌟⭐🎯🎨🏆🥇🎁🎈]+'
)

# All emoji pattern
ALL_EMOJIS = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F000-\U0001F02F"
    "\U0001F0A0-\U0001F0FF"
    "\U0001F100-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "]+",
    flags=re.UNICODE
)


def is_in_code_block(line: str, in_block: bool) -> bool:
    """Check if we're inside a code block."""
    if line.strip().startswith('```'):
        return not in_block
    return in_block


def replace_emojis_in_line(line: str, in_code_block: bool) -> Tuple[str, List[Dict]]:
    """Replace emojis in a line with text equivalents."""
    if in_code_block:
        return line, []

    changes = []
    new_line = line

    # First, replace known status emojis
    for emoji, replacement in STATUS_REPLACEMENTS.items():
        if emoji in new_line:
            count = new_line.count(emoji)
            new_line = new_line.replace(emoji, replacement)
            for _ in range(count):
                changes.append({
                    'emoji': emoji,
                    'replacement': replacement,
                    'type': 'status'
                })

    # Then remove decorative emojis
    decorative_matches = DECORATIVE_EMOJIS.findall(new_line)
    for match in decorative_matches:
        new_line = new_line.replace(match, '')
        changes.append({
            'emoji': match,
            'replacement': '(removed)',
            'type': 'decorative'
        })

    # Finally, catch any remaining emojis and remove them
    remaining_matches = ALL_EMOJIS.findall(new_line)
    for match in remaining_matches:
        # Skip if already handled
        if match in STATUS_REPLACEMENTS or DECORATIVE_EMOJIS.match(match):
            continue
        new_line = new_line.replace(match, '')
        changes.append({
            'emoji': match,
            'replacement': '(removed)',
            'type': 'other'
        })

    # Clean up double spaces
    new_line = re.sub(r'  +', ' ', new_line)

    return new_line, changes


def process_file(filepath: Path, apply: bool = False) -> Dict:
    """Process a single file and return changes."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError) as e:
        return {'error': str(e)}

    new_lines = []
    all_changes = []
    in_code_block = False

    for line_num, line in enumerate(lines, 1):
        in_code_block = is_in_code_block(line, in_code_block)
        new_line, changes = replace_emojis_in_line(line, in_code_block)

        if changes:
            all_changes.append({
                'line_num': line_num,
                'original': line.rstrip(),
                'modified': new_line.rstrip(),
                'changes': changes
            })

        new_lines.append(new_line)

    if apply and all_changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return {
        'changes': all_changes,
        'total_emojis': sum(len(c['changes']) for c in all_changes)
    }


def process_directory(directory: Path, extensions: List[str], apply: bool = False) -> Dict:
    """Process all files in directory."""
    results = {}

    for ext in extensions:
        for filepath in directory.rglob(f"*{ext}"):
            # Skip hidden files
            if any(part.startswith('.') for part in filepath.parts):
                continue

            result = process_file(filepath, apply)
            if result.get('changes'):
                results[str(filepath.relative_to(directory))] = result

    return results


def generate_report(results: Dict, apply: bool = False) -> str:
    """Generate a human-readable report."""
    total_files = len(results)
    total_emojis = sum(r['total_emojis'] for r in results.values() if 'total_emojis' in r)

    report = ["# Emoji Removal Report\n"]

    if apply:
        report.append("**Status:** Changes applied")
    else:
        report.append("**Status:** Dry run (no changes made)")

    report.append(f"**Files processed:** {total_files}")
    report.append(f"**Total emojis removed:** {total_emojis}\n")

    if not results:
        report.append("No emojis found!")
        return "\n".join(report)

    # Categorize by type
    status_count = 0
    decorative_count = 0
    other_count = 0

    for file_result in results.values():
        for change in file_result.get('changes', []):
            for c in change['changes']:
                if c['type'] == 'status':
                    status_count += 1
                elif c['type'] == 'decorative':
                    decorative_count += 1
                else:
                    other_count += 1

    report.append("## Summary by Type\n")
    report.append(f"- Status indicators converted: {status_count}")
    report.append(f"- Decorative emojis removed: {decorative_count}")
    report.append(f"- Other emojis removed: {other_count}\n")

    report.append("## Changes by File\n")

    for filepath, file_result in sorted(results.items()):
        if 'error' in file_result:
            report.append(f"### {filepath}\n")
            report.append(f"Error: {file_result['error']}\n")
            continue

        changes = file_result.get('changes', [])
        if not changes:
            continue

        report.append(f"### {filepath} ({file_result['total_emojis']} emojis)\n")

        # Show first 10 changes
        for change in changes[:10]:
            line_num = change['line_num']
            for c in change['changes']:
                report.append(
                    f"- Line {line_num}: `{c['emoji']}` → {c['replacement']}"
                )

        if len(changes) > 10:
            report.append(f"  ... and {len(changes) - 10} more changes\n")
        else:
            report.append("")

    if not apply:
        report.append("\n## Next Steps\n")
        report.append("Run with `--apply` to make these changes permanent.")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Remove emojis from text files")
    parser.add_argument("directory", type=Path, help="Directory to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without applying")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".md", ".txt"],
        help="File extensions to process (default: .md .txt)"
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory {args.directory} does not exist", file=sys.stderr)
        sys.exit(1)

    apply = args.apply and not args.dry_run

    results = process_directory(args.directory, args.extensions, apply)

    if args.json:
        output = {
            'applied': apply,
            'total_files': len(results),
            'total_emojis': sum(r['total_emojis'] for r in results.values() if 'total_emojis' in r),
            'files': results
        }
        print(json.dumps(output, indent=2))
    else:
        report = generate_report(results, apply)
        print(report)


if __name__ == "__main__":
    main()
