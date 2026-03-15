#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""
Validate SKILL.md frontmatter across all skills.

Checks for:
- Required frontmatter fields (name, description, allowed-tools)
- Valid tool references
- Valid skill references
- Consistent formatting
- Common issues and best practices
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import yaml

# Valid Claude Code tools
VALID_TOOLS = {
    'Agent', 'Bash', 'Read', 'Write', 'Edit', 'Glob', 'Grep',
    'WebFetch', 'WebSearch', 'TaskCreate', 'TaskUpdate', 'TaskGet',
    'TaskList', 'TaskOutput', 'TaskStop', 'AskUserQuestion',
    'EnterPlanMode', 'ExitPlanMode', 'Skill', 'NotebookEdit',
    'EnterWorktree', 'LSP', 'MultiEdit', 'TodoWrite'
}

# Valid hook types
VALID_HOOKS = {
    'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'SessionStart'
}


class SkillValidator:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.errors = []
        self.warnings = []
        self.skills_map = {}  # name -> path mapping

    def find_all_skills(self) -> List[Path]:
        """Find all SKILL.md files recursively."""
        return list(self.skills_dir.rglob('SKILL.md'))

    def parse_frontmatter(self, file_path: Path) -> Tuple[Optional[Dict], str]:
        """Extract and parse YAML frontmatter from SKILL.md file."""
        content = file_path.read_text()

        # Check for frontmatter
        if not content.startswith('---\n'):
            return None, content

        # Extract frontmatter
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return None, content

        frontmatter_str = parts[1]
        body = parts[2]

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter, body
        except yaml.YAMLError as e:
            self.errors.append(f"{file_path}: Invalid YAML frontmatter: {e}")
            return None, body

    def validate_required_fields(self, file_path: Path, fm: Dict) -> None:
        """Check for required frontmatter fields."""
        required = ['name', 'description']

        for field in required:
            if field not in fm or not fm[field]:
                self.errors.append(f"{file_path}: Missing required field '{field}'")

        # allowed-tools is recommended but not strictly required
        if 'allowed-tools' not in fm:
            self.warnings.append(f"{file_path}: Missing 'allowed-tools' field (recommended)")

    def validate_tools(self, file_path: Path, fm: Dict) -> None:
        """Validate tool references."""
        if 'allowed-tools' not in fm:
            return

        tools = fm['allowed-tools']
        if not isinstance(tools, list):
            self.errors.append(f"{file_path}: 'allowed-tools' must be a list")
            return

        for tool in tools:
            if tool not in VALID_TOOLS:
                self.warnings.append(f"{file_path}: Unknown tool '{tool}' (might be MCP tool)")

    def validate_skills(self, file_path: Path, fm: Dict) -> None:
        """Validate skill references."""
        if 'skills' not in fm:
            return

        skills = fm['skills']

        # Can be string (single skill) or list
        if isinstance(skills, str):
            skills = [skills]
        elif not isinstance(skills, list):
            self.errors.append(f"{file_path}: 'skills' must be a string or list")
            return

        # We'll validate these exist in a second pass
        for skill in skills:
            if not isinstance(skill, str):
                self.errors.append(f"{file_path}: Skill reference must be string, got {type(skill)}")

    def validate_hooks(self, file_path: Path, fm: Dict) -> None:
        """Validate hook references."""
        if 'hooks' not in fm:
            return

        hooks = fm['hooks']
        if not isinstance(hooks, list):
            self.errors.append(f"{file_path}: 'hooks' must be a list")
            return

        for hook in hooks:
            if not isinstance(hook, dict):
                self.errors.append(f"{file_path}: Hook must be a dict with 'event' and 'command'")
                continue

            if 'event' not in hook:
                self.errors.append(f"{file_path}: Hook missing 'event' field")
            elif hook['event'] not in VALID_HOOKS:
                self.errors.append(f"{file_path}: Invalid hook event '{hook['event']}'")

            if 'command' not in hook:
                self.errors.append(f"{file_path}: Hook missing 'command' field")

    def validate_description(self, file_path: Path, fm: Dict) -> None:
        """Check description quality."""
        if 'description' not in fm:
            return

        desc = fm['description']

        # Check length
        if len(desc) < 50:
            self.warnings.append(f"{file_path}: Description is very short ({len(desc)} chars)")

        # Check if it includes trigger phrases or use cases
        if 'use when' not in desc.lower() and 'trigger' not in desc.lower():
            self.warnings.append(f"{file_path}: Description should include trigger phrases or use cases")

    def validate_naming(self, file_path: Path, fm: Dict) -> None:
        """Check naming conventions."""
        if 'name' not in fm:
            return

        name = fm['name']

        # Check for valid characters (lowercase, hyphens, colons for namespaces)
        if not re.match(r'^[a-z0-9\-:]+$', name):
            self.warnings.append(f"{file_path}: Name should use lowercase, hyphens, and colons only")

        # Store for cross-reference validation
        self.skills_map[name] = file_path

    def validate_skill_file(self, file_path: Path) -> None:
        """Validate a single SKILL.md file."""
        # Parse frontmatter
        frontmatter, body = self.parse_frontmatter(file_path)

        if frontmatter is None:
            self.errors.append(f"{file_path}: No frontmatter found or invalid YAML")
            return

        # Run all validations
        self.validate_required_fields(file_path, frontmatter)
        self.validate_naming(file_path, frontmatter)
        self.validate_description(file_path, frontmatter)
        self.validate_tools(file_path, frontmatter)
        self.validate_skills(file_path, frontmatter)
        self.validate_hooks(file_path, frontmatter)

    def validate_cross_references(self) -> None:
        """Validate that referenced skills actually exist."""
        for skill_path in self.find_all_skills():
            frontmatter, _ = self.parse_frontmatter(skill_path)
            if not frontmatter or 'skills' not in frontmatter:
                continue

            skills = frontmatter['skills']
            if isinstance(skills, str):
                # Handle comma-separated skills
                skills = [s.strip() for s in skills.split(',')]
            elif not isinstance(skills, list):
                continue

            for referenced_skill in skills:
                if referenced_skill not in self.skills_map:
                    self.warnings.append(
                        f"{skill_path}: References unknown skill '{referenced_skill}'"
                    )

    def run(self) -> int:
        """Run validation on all SKILL.md files."""
        skill_files = self.find_all_skills()

        if not skill_files:
            print(f"No SKILL.md files found in {self.skills_dir}")
            return 1

        print(f"Found {len(skill_files)} SKILL.md files\n")

        # First pass: validate each file
        for skill_file in skill_files:
            self.validate_skill_file(skill_file)

        # Second pass: cross-reference validation
        self.validate_cross_references()

        # Report results
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("✅ All SKILL.md files are valid!")
            return 0

        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        return 1 if self.errors else 0


def main():
    # Default to ~/.claude/skills
    skills_dir = Path.home() / '.claude' / 'skills'

    # Allow override via argument
    if len(sys.argv) > 1:
        skills_dir = Path(sys.argv[1])

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    validator = SkillValidator(skills_dir)
    return validator.run()


if __name__ == '__main__':
    sys.exit(main())
