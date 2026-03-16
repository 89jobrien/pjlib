#!/usr/bin/env -S uv run
# /// script
# dependencies = []
# ///
"""
Interactive skill template generator.

Creates a new Claude Code skill with proper frontmatter and structure.
"""

import sys
import re
from pathlib import Path
from typing import List, Optional

# Valid Claude Code tools
COMMON_TOOLS = [
    'Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash',
    'Agent', 'WebFetch', 'WebSearch', 'AskUserQuestion',
    'TaskCreate', 'TaskUpdate', 'TaskList', 'EnterPlanMode'
]


class SkillGenerator:
    def __init__(self):
        self.name = None
        self.description = None
        self.tools = []
        self.related_skills = []
        self.output_dir = None

    def prompt_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Prompt for user input with optional default."""
        if default:
            result = input(f"{prompt} [{default}]: ").strip()
            return result if result else default
        else:
            while True:
                result = input(f"{prompt}: ").strip()
                if result:
                    return result
                print("This field is required.")

    def prompt_multiline(self, prompt: str) -> str:
        """Prompt for multi-line input (ended with empty line)."""
        print(f"{prompt}")
        print("(Enter an empty line when done)")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        return ' '.join(lines)

    def prompt_list(self, prompt: str, options: List[str]) -> List[str]:
        """Prompt for selecting multiple items from a list."""
        print(f"\n{prompt}")
        print("Available options:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print("\nEnter numbers separated by commas (e.g., 1,3,5) or 'all':")

        while True:
            selection = input("> ").strip().lower()

            if selection == 'all':
                return options

            if not selection:
                return []

            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected = [options[i] for i in indices if 0 <= i < len(options)]
                return selected
            except (ValueError, IndexError):
                print("Invalid selection. Try again or press Enter to skip.")

    def validate_name(self, name: str) -> bool:
        """Validate skill name format."""
        if not re.match(r'^[a-z0-9\-:]+$', name):
            print("❌ Name should use lowercase, hyphens, and colons only")
            return False
        return True

    def generate_frontmatter(self) -> str:
        """Generate YAML frontmatter."""
        lines = ["---"]
        lines.append(f"name: {self.name}")
        lines.append(f"description: {self.description}")

        if self.tools:
            tools_str = ', '.join(self.tools)
            lines.append(f"allowed-tools: [{tools_str}]")

        if self.related_skills:
            skills_str = ', '.join(self.related_skills)
            lines.append(f"skills: {skills_str}")

        lines.append("---")
        return '\n'.join(lines)

    def generate_skill_content(self) -> str:
        """Generate complete SKILL.md content."""
        frontmatter = self.generate_frontmatter()

        # Convert name to title case for heading
        title = self.name.replace('-', ' ').replace(':', ' - ').title()

        content = f"""{frontmatter}

# {title}

{self.description}

## When to Use

Use this skill when:
- [Add specific trigger conditions]
- [Add use cases]
- [Add scenarios]

## What This Skill Does

1. **[Main Function]**: [Description]
2. **[Secondary Function]**: [Description]

## How to Use

```bash
# Basic usage
/{self.name}

# With arguments
/{self.name} [options]
```

## Examples

### Example 1: [Use Case]

**Input**: [Description of input]

**Output**:
```
[Example output]
```

### Example 2: [Another Use Case]

**Input**: [Description of input]

**Output**:
```
[Example output]
```

## Best Practices

- [Practice 1]
- [Practice 2]
- [Practice 3]

## Related Use Cases

- [Related use case 1]
- [Related use case 2]
"""
        return content

    def create_skill_structure(self):
        """Create skill directory and files."""
        skill_path = self.output_dir / self.name
        skill_path.mkdir(parents=True, exist_ok=True)

        # Create SKILL.md
        skill_md = skill_path / "SKILL.md"
        skill_md.write_text(self.generate_skill_content())

        # Create optional directories
        (skill_path / "scripts").mkdir(exist_ok=True)
        (skill_path / "scripts" / ".gitkeep").touch()

        (skill_path / "references").mkdir(exist_ok=True)
        (skill_path / "references" / ".gitkeep").touch()

        return skill_path

    def run(self):
        """Run interactive skill generator."""
        print("═" * 60)
        print("Claude Code Skill Generator")
        print("═" * 60)
        print()

        # Determine output directory
        default_dir = Path.home() / '.claude' / 'skills'
        output = self.prompt_input(
            "Output directory",
            str(default_dir)
        )
        self.output_dir = Path(output)

        if not self.output_dir.exists():
            create = input(f"Directory {self.output_dir} doesn't exist. Create it? [y/N]: ")
            if create.lower() == 'y':
                self.output_dir.mkdir(parents=True)
            else:
                print("Cancelled.")
                return 1

        # Skill name
        while True:
            name = self.prompt_input("Skill name (lowercase, hyphens)")
            if self.validate_name(name):
                self.name = name
                break

        # Description
        self.description = self.prompt_multiline(
            "\nSkill description (include use cases and triggers)"
        )

        # Tools
        print("\n")
        self.tools = self.prompt_list(
            "Select allowed tools:",
            COMMON_TOOLS
        )

        # Related skills
        custom_skills = input("\nRelated skills (comma-separated, or Enter to skip): ").strip()
        if custom_skills:
            self.related_skills = [s.strip() for s in custom_skills.split(',')]

        # Generate skill
        print("\n" + "─" * 60)
        print("Generating skill...")
        print("─" * 60)

        try:
            skill_path = self.create_skill_structure()
            print(f"\n✅ Created skill at: {skill_path}")
            print(f"\n📝 Edit SKILL.md to customize:")
            print(f"   {skill_path}/SKILL.md")
            print(f"\n📁 Add resources to:")
            print(f"   {skill_path}/scripts/    - Helper scripts")
            print(f"   {skill_path}/references/ - Documentation")
            return 0
        except Exception as e:
            print(f"\n❌ Error creating skill: {e}")
            return 1


def main():
    generator = SkillGenerator()
    return generator.run()


if __name__ == '__main__':
    sys.exit(main())
