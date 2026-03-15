#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""
Comprehensive skill quality linter.

Checks for:
- Frontmatter validation (via validate-skills)
- Content quality (structure, completeness)
- Code quality in scripts
- Reference quality
- Best practices compliance
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import subprocess
import yaml


class SkillLinter:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.errors = []
        self.warnings = []
        self.info = []

    def find_all_skills(self) -> List[Path]:
        """Find all SKILL.md files recursively."""
        return list(self.skills_dir.rglob('SKILL.md'))

    def parse_frontmatter(self, file_path: Path) -> tuple[Optional[Dict], str]:
        """Extract and parse YAML frontmatter."""
        content = file_path.read_text()

        if not content.startswith('---\n'):
            return None, content

        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return None, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            return frontmatter, parts[2]
        except yaml.YAMLError:
            return None, parts[2]

    def check_content_structure(self, file_path: Path, body: str) -> None:
        """Check SKILL.md content structure and quality."""
        # Required sections
        required_sections = [
            r'## When to Use',
            r'## What This Skill Does',
            r'## How to Use'
        ]

        for section in required_sections:
            if not re.search(section, body, re.IGNORECASE):
                self.warnings.append(
                    f"{file_path}: Missing recommended section '{section}'"
                )

        # Check for examples section
        if not re.search(r'## Examples?', body, re.IGNORECASE):
            self.warnings.append(
                f"{file_path}: Missing Examples section (recommended)"
            )

        # Check for empty sections
        sections = re.findall(r'^##\s+(.+)$', body, re.MULTILINE)
        for section in sections:
            # Check if there's content after this section
            pattern = f'## {re.escape(section)}\\s*\\n\\s*(?:##|$)'
            if re.search(pattern, body):
                self.warnings.append(
                    f"{file_path}: Section '{section}' appears to be empty"
                )

    def check_scripts(self, skill_dir: Path) -> None:
        """Check quality of bundled scripts."""
        scripts_dir = skill_dir / 'scripts'
        if not scripts_dir.exists():
            return

        for script_file in scripts_dir.rglob('*'):
            if script_file.is_file() and script_file.suffix in ['.py', '.sh', '.bash']:
                # Check for shebang
                content = script_file.read_text()
                if not content.startswith('#!'):
                    self.warnings.append(
                        f"{script_file}: Missing shebang line"
                    )

                # Check if executable
                if not script_file.stat().st_mode & 0o111:
                    self.warnings.append(
                        f"{script_file}: Not executable (chmod +x needed)"
                    )

                # Check for documentation
                if script_file.suffix == '.py':
                    if not re.search(r'""".*"""', content, re.DOTALL):
                        self.warnings.append(
                            f"{script_file}: Missing module docstring"
                        )

    def check_references(self, skill_dir: Path) -> None:
        """Check quality of reference documentation."""
        refs_dir = skill_dir / 'references'
        if not refs_dir.exists():
            return

        for ref_file in refs_dir.rglob('*.md'):
            content = ref_file.read_text()

            # Check for frontmatter in references
            if not content.startswith('---\n'):
                self.info.append(
                    f"{ref_file}: Reference could benefit from frontmatter"
                )

            # Check for title
            if not re.search(r'^#\s+.+', content, re.MULTILINE):
                self.warnings.append(
                    f"{ref_file}: Missing top-level heading"
                )

    def check_best_practices(self, file_path: Path, frontmatter: Dict, body: str) -> None:
        """Check adherence to skill best practices."""
        skill_dir = file_path.parent

        # Check for bundled resources mention
        if (skill_dir / 'scripts').exists():
            scripts = list((skill_dir / 'scripts').rglob('*'))
            if scripts and not re.search(r'scripts?/', body, re.IGNORECASE):
                self.info.append(
                    f"{file_path}: Has scripts/ but doesn't mention them in SKILL.md"
                )

        if (skill_dir / 'references').exists():
            refs = list((skill_dir / 'references').rglob('*.md'))
            if refs and not re.search(r'references?/', body, re.IGNORECASE):
                self.info.append(
                    f"{file_path}: Has references/ but doesn't mention them in SKILL.md"
                )

        # Check for clear use cases in description
        if frontmatter and 'description' in frontmatter:
            desc = frontmatter['description'].lower()
            has_triggers = any(word in desc for word in ['when', 'use', 'trigger', 'for'])

            if not has_triggers:
                self.warnings.append(
                    f"{file_path}: Description should include trigger words (when/use/for)"
                )

        # Check for overly generic names
        if frontmatter and 'name' in frontmatter:
            name = frontmatter['name']
            generic_names = ['helper', 'utility', 'tool', 'general']
            if any(gen in name.lower() for gen in generic_names):
                self.info.append(
                    f"{file_path}: Name '{name}' might be too generic"
                )

    def check_consistency(self, file_path: Path, body: str) -> None:
        """Check for consistency issues."""
        # Check for consistent code block formatting
        code_blocks = re.findall(r'```(\w*)', body)
        if code_blocks:
            # Check for unlabeled code blocks
            unlabeled = code_blocks.count('')
            if unlabeled > 0:
                self.warnings.append(
                    f"{file_path}: {unlabeled} code block(s) without language label"
                )

        # Check for broken internal links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body)
        for link_text, link_url in links:
            # Skip external links
            if link_url.startswith(('http://', 'https://', '#')):
                continue

            # Check if file exists
            target = file_path.parent / link_url
            if not target.exists():
                self.warnings.append(
                    f"{file_path}: Broken link to '{link_url}'"
                )

    def lint_skill(self, file_path: Path) -> None:
        """Lint a single skill."""
        frontmatter, body = self.parse_frontmatter(file_path)

        if frontmatter is None:
            return  # Skip, will be caught by validator

        skill_dir = file_path.parent

        # Run all checks
        self.check_content_structure(file_path, body)
        self.check_scripts(skill_dir)
        self.check_references(skill_dir)
        self.check_best_practices(file_path, frontmatter, body)
        self.check_consistency(file_path, body)

    def run(self) -> int:
        """Run linter on all skills."""
        skill_files = self.find_all_skills()

        if not skill_files:
            print(f"No SKILL.md files found in {self.skills_dir}")
            return 1

        print(f"Linting {len(skill_files)} skills...\n")

        for skill_file in skill_files:
            self.lint_skill(skill_file)

        # Report results
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.info:
            print(f"\nINFO ({len(self.info)}):")
            for info in self.info:
                print(f"  • {info}")

        if not self.errors and not self.warnings and not self.info:
            print("All skills pass quality checks!")
            return 0

        print(f"\nSummary: {len(self.errors)} errors, {len(self.warnings)} warnings, {len(self.info)} suggestions")
        return 1 if self.errors else 0


def main():
    # Default to ~/.claude/skills
    skills_dir = Path.home() / '.claude' / 'skills'

    if len(sys.argv) > 1:
        skills_dir = Path(sys.argv[1])

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    linter = SkillLinter(skills_dir)
    return linter.run()


if __name__ == '__main__':
    sys.exit(main())
