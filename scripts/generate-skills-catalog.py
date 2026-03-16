#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml",
# ]
# ///
"""
Generate a comprehensive skills catalog from SKILL.md frontmatter.

Creates markdown documentation with:
- Alphabetical index
- Category grouping
- Tool usage matrix
- Skill dependency graph
"""

import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
import yaml


class SkillCatalog:
    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        self.skills = []

    def find_all_skills(self) -> List[Path]:
        """Find all SKILL.md files recursively."""
        return sorted(self.skills_dir.rglob('SKILL.md'))

    def parse_skill(self, file_path: Path) -> Optional[Dict]:
        """Parse a single SKILL.md file."""
        try:
            content = file_path.read_text()

            if not content.startswith('---\n'):
                return None

            parts = content.split('---\n', 2)
            if len(parts) < 3:
                return None

            frontmatter = yaml.safe_load(parts[1])

            # Extract first paragraph from body as summary
            body_lines = parts[2].strip().split('\n')
            summary = None
            for line in body_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    summary = line
                    break

            return {
                'path': file_path,
                'relative_path': file_path.relative_to(self.skills_dir),
                'name': frontmatter.get('name', ''),
                'description': frontmatter.get('description', ''),
                'summary': summary,
                'tools': frontmatter.get('allowed-tools', []),
                'skills': self._parse_skills_list(frontmatter.get('skills', [])),
                'hooks': frontmatter.get('hooks', [])
            }
        except Exception as e:
            print(f"Warning: Failed to parse {file_path}: {e}", file=sys.stderr)
            return None

    def _parse_skills_list(self, skills) -> List[str]:
        """Parse skills field (can be string or list)."""
        if isinstance(skills, str):
            return [s.strip() for s in skills.split(',')]
        elif isinstance(skills, list):
            return skills
        return []

    def load_all_skills(self):
        """Load all skills into memory."""
        for skill_file in self.find_all_skills():
            skill = self.parse_skill(skill_file)
            if skill and skill['name']:
                self.skills.append(skill)

        # Sort by name
        self.skills.sort(key=lambda s: s['name'])

    def generate_alphabetical_index(self) -> str:
        """Generate alphabetical index section."""
        lines = ["## Alphabetical Index\n"]

        for skill in self.skills:
            name = skill['name']
            desc = skill['description'][:100] + '...' if len(skill['description']) > 100 else skill['description']
            lines.append(f"### {name}\n")
            lines.append(f"{desc}\n")

            if skill['tools']:
                tools_str = ', '.join(f"`{t}`" for t in skill['tools'])
                lines.append(f"**Tools:** {tools_str}\n")

            if skill['skills']:
                skills_str = ', '.join(f"`{s}`" for s in skill['skills'])
                lines.append(f"**Related Skills:** {skills_str}\n")

            lines.append("")

        return '\n'.join(lines)

    def generate_tool_matrix(self) -> str:
        """Generate tool usage matrix."""
        lines = ["## Tool Usage Matrix\n"]
        lines.append("Shows which tools are used by each skill:\n")

        # Collect all unique tools
        all_tools = set()
        for skill in self.skills:
            all_tools.update(skill['tools'])

        all_tools = sorted(all_tools)

        if not all_tools:
            return ""

        # Create table header
        lines.append("| Skill | " + " | ".join(all_tools) + " |")
        lines.append("|" + "---|" * (len(all_tools) + 1))

        # Create rows
        for skill in self.skills:
            skill_tools = set(skill['tools'])
            row = [skill['name']]

            for tool in all_tools:
                row.append("✓" if tool in skill_tools else "")

            lines.append("| " + " | ".join(row) + " |")

        return '\n'.join(lines)

    def generate_dependency_graph(self) -> str:
        """Generate skill dependency information."""
        lines = ["## Skill Dependencies\n"]
        lines.append("Shows which skills reference other skills:\n")

        # Build dependency map
        dependencies = defaultdict(list)
        dependents = defaultdict(list)

        for skill in self.skills:
            name = skill['name']
            for dep in skill['skills']:
                dependencies[name].append(dep)
                dependents[dep].append(name)

        # List skills with dependencies
        has_deps = False
        for skill in self.skills:
            name = skill['name']
            if dependencies[name] or dependents[name]:
                has_deps = True
                lines.append(f"### {name}\n")

                if dependencies[name]:
                    deps_str = ', '.join(f"`{d}`" for d in dependencies[name])
                    lines.append(f"**Uses:** {deps_str}\n")

                if dependents[name]:
                    deps_str = ', '.join(f"`{d}`" for d in dependents[name])
                    lines.append(f"**Used by:** {deps_str}\n")

                lines.append("")

        if not has_deps:
            lines.append("No skill dependencies found.\n")

        return '\n'.join(lines)

    def generate_categories(self) -> str:
        """Generate skills organized by category (from name prefix)."""
        lines = ["## Skills by Category\n"]

        # Group by category (before first colon)
        categories = defaultdict(list)

        for skill in self.skills:
            name = skill['name']
            if ':' in name:
                category = name.split(':', 1)[0]
            else:
                category = 'General'

            categories[category].append(skill)

        # Sort categories
        for category in sorted(categories.keys()):
            lines.append(f"### {category.title()}\n")

            for skill in categories[category]:
                name = skill['name']
                desc = skill['description'][:80] + '...' if len(skill['description']) > 80 else skill['description']
                lines.append(f"- **{name}**: {desc}")

            lines.append("")

        return '\n'.join(lines)

    def generate_statistics(self) -> str:
        """Generate statistics section."""
        lines = ["## Statistics\n"]

        total = len(self.skills)
        lines.append(f"- **Total Skills:** {total}")

        # Count by category
        categories = defaultdict(int)
        for skill in self.skills:
            name = skill['name']
            category = name.split(':', 1)[0] if ':' in name else 'General'
            categories[category] += 1

        lines.append(f"- **Categories:** {len(categories)}")

        # Most common tools
        tool_counts = defaultdict(int)
        for skill in self.skills:
            for tool in skill['tools']:
                tool_counts[tool] += 1

        if tool_counts:
            top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            lines.append("\n**Most Used Tools:**")
            for tool, count in top_tools:
                lines.append(f"- `{tool}`: {count} skills")

        return '\n'.join(lines)

    def generate_catalog(self) -> str:
        """Generate complete catalog."""
        lines = [
            "# Claude Code Skills Catalog\n",
            f"*Generated from {len(self.skills)} skills*\n",
            "---\n"
        ]

        # Add statistics
        lines.append(self.generate_statistics())
        lines.append("\n---\n")

        # Add categories
        lines.append(self.generate_categories())
        lines.append("\n---\n")

        # Add alphabetical index
        lines.append(self.generate_alphabetical_index())
        lines.append("\n---\n")

        # Add dependencies
        lines.append(self.generate_dependency_graph())
        lines.append("\n---\n")

        # Add tool matrix
        lines.append(self.generate_tool_matrix())

        return '\n'.join(lines)

    def run(self, output_file: Optional[Path] = None) -> int:
        """Generate catalog and optionally save to file."""
        skill_files = self.find_all_skills()

        if not skill_files:
            print(f"No SKILL.md files found in {self.skills_dir}")
            return 1

        print(f"Loading {len(skill_files)} skills...")
        self.load_all_skills()

        print(f"Generating catalog for {len(self.skills)} valid skills...")
        catalog = self.generate_catalog()

        if output_file:
            output_file.write_text(catalog)
            print(f"✅ Catalog written to: {output_file}")
        else:
            print(catalog)

        return 0


def main():
    # Default to ~/.claude/skills
    skills_dir = Path.home() / '.claude' / 'skills'
    output_file = None

    # Parse arguments
    if len(sys.argv) > 1:
        skills_dir = Path(sys.argv[1])

    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        # Default output location
        output_file = skills_dir.parent / 'SKILLS_CATALOG.md'

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return 1

    catalog = SkillCatalog(skills_dir)
    return catalog.run(output_file)


if __name__ == '__main__':
    sys.exit(main())
