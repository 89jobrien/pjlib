"""Setup hooks for environment validation and workspace initialization.

Provides on-demand setup capabilities:
- Environment validation (tools, versions, env vars)
- Workspace initialization (directories, configs)
- Dependency management (check/install packages)
- Project scaffolding (detect and configure projects)
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add hooks root to path for imports
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error


@dataclass
class SetupReport:
    """Comprehensive setup validation report."""

    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    validations: list[ValidationResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if all validations passed (warnings allowed)."""
        return self.checks_failed == 0

    def add(self, result: ValidationResult) -> None:
        """Add a validation result to the report."""
        self.validations.append(result)
        if result.passed:
            self.checks_passed += 1
        elif result.severity == "warning":
            self.checks_warned += 1
        else:
            self.checks_failed += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for JSON output."""
        return {
            "success": self.success,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "checks_warned": self.checks_warned,
            "validations": [
                {
                    "passed": v.passed,
                    "message": v.message,
                    "details": v.details,
                    "severity": v.severity,
                }
                for v in self.validations
            ],
        }


def load_setup_config() -> dict[str, Any]:
    """Load setup configuration from hooks_config.yaml.

    Returns:
        Setup configuration dict
    """
    try:
        import yaml

        config_path = HOOKS_ROOT / "hooks_config.yaml"
        if not config_path.exists():
            return {}

        with config_path.open() as f:
            config = yaml.safe_load(f) or {}
            return config.get("setup", {})
    except Exception:
        return {}


def get_env_var(name: str, default: str | None = None) -> str | None:
    """Get environment variable value.

    Args:
        name: Environment variable name
        default: Default value if not set

    Returns:
        Environment variable value or default
    """
    return os.environ.get(name, default)


def check_env_var(name: str) -> ValidationResult:
    """Check if environment variable is set.

    Args:
        name: Environment variable name

    Returns:
        ValidationResult
    """
    value = get_env_var(name)
    if value:
        return ValidationResult(
            passed=True,
            message=f"Environment variable {name} is set",
            details={"name": name, "value": value[:50] if len(value) > 50 else value},
        )
    return ValidationResult(
        passed=False,
        message=f"Environment variable {name} is not set",
        details={"name": name},
        severity="error",
    )
