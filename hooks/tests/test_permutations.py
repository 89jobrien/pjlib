#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pytest"]
# ///
"""
Code Permutation Tests for JIT Context and TODO Tracker hooks.

Tests multiple implementation variations for:
- Pattern matching strategies
- File I/O approaches
- Search algorithms
- Memory efficiency
"""
from __future__ import annotations

import re
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ============================================================================
# VARIATION 1: Pattern Extraction Strategies (jit_context.py)
# ============================================================================


def extract_patterns_v1_regex(prompt: str) -> list[str]:
    """Original: Two separate regex passes."""
    patterns: list[str] = []
    glob_pattern = re.compile(r"[*?[\]{}]+[.\w/]*|[\w./]+[*?[\]{}]+[\w./]*")
    for match in glob_pattern.findall(prompt):
        if match.strip():
            patterns.append(match.strip())
    ext_pattern = re.compile(r"\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml|toml|sh|sql)\b")
    for ext in ext_pattern.findall(prompt):
        patterns.append(f"*{ext}")
    return list(set(patterns))


def extract_patterns_v2_combined(prompt: str) -> list[str]:
    """Variation 2: Single combined regex."""
    patterns: list[str] = []
    combined = re.compile(
        r"([*?[\]{}]+[.\w/]*|[\w./]+[*?[\]{}]+[\w./]*)"
        r"|"
        r"(\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml|toml|sh|sql))\b"
    )
    for m in combined.finditer(prompt):
        if m.group(1):
            patterns.append(m.group(1).strip())
        elif m.group(2):
            patterns.append(f"*{m.group(2)}")
    return list(set(patterns))


def extract_patterns_v3_precompiled(
    prompt: str,
    _glob_re: re.Pattern[str] = re.compile(r"[*?[\]{}]+[.\w/]*|[\w./]+[*?[\]{}]+[\w./]*"),
    _ext_re: re.Pattern[str] = re.compile(r"\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml|toml|sh|sql)\b"),
) -> list[str]:
    """Variation 3: Pre-compiled regex as default args."""
    patterns: list[str] = []
    for match in _glob_re.findall(prompt):
        if match.strip():
            patterns.append(match.strip())
    for ext in _ext_re.findall(prompt):
        patterns.append(f"*{ext}")
    return list(set(patterns))


# ============================================================================
# VARIATION 2: File Reading Strategies (jit_context.py)
# ============================================================================


def head_tail_v1_readall(path: Path, head: int = 30, tail: int = 20) -> str:
    """Original: Read entire file then slice."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        total = len(lines)
        if total <= head + tail:
            return text
        return f"{chr(10).join(lines[:head])}\n\n... [{total - head - tail} lines omitted] ...\n\n{chr(10).join(lines[-tail:])}"
    except Exception:
        return ""


def head_tail_v2_streaming(path: Path, head: int = 30, tail: int = 20) -> str:
    """Variation 2: Stream file to reduce memory."""
    try:
        head_lines: list[str] = []
        tail_buffer: list[str] = []
        total = 0
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total += 1
                if len(head_lines) < head:
                    head_lines.append(line.rstrip("\n"))
                else:
                    tail_buffer.append(line.rstrip("\n"))
                    if len(tail_buffer) > tail:
                        tail_buffer.pop(0)
        if total <= head + tail:
            return "\n".join(head_lines + tail_buffer)
        omitted = total - head - tail
        return f"{chr(10).join(head_lines)}\n\n... [{omitted} lines omitted] ...\n\n{chr(10).join(tail_buffer)}"
    except Exception:
        return ""


def head_tail_v3_mmap(path: Path, head: int = 30, tail: int = 20) -> str:
    """Variation 3: Memory-mapped for large files."""
    import mmap

    try:
        size = path.stat().st_size
        if size < 10000:  # Small files: just read normally
            return head_tail_v1_readall(path, head, tail)
        with path.open("r+b") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                content = mm[:].decode("utf-8", errors="ignore")
        lines = content.splitlines()
        total = len(lines)
        if total <= head + tail:
            return content
        return f"{chr(10).join(lines[:head])}\n\n... [{total - head - tail} lines omitted] ...\n\n{chr(10).join(lines[-tail:])}"
    except Exception:
        return head_tail_v1_readall(path, head, tail)


# ============================================================================
# VARIATION 3: TODO Pattern Matching (todo_tracker.py)
# ============================================================================

TODO_PATTERNS_V1 = [
    r"#\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)$",
    r"//\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)$",
    r"/\*\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)\*/",
    r"<!--\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)-->",
]


def extract_todos_v1_multipass(content: str) -> list[tuple[str, str, int]]:
    """Original: Try each pattern per line."""
    todos = []
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        for pattern in TODO_PATTERNS_V1:
            match = re.search(pattern, line, re.IGNORECASE | re.MULTILINE)
            if match:
                todos.append((match.group(1).upper(), match.group(2).strip(), i))
                break
    return todos


TODO_COMBINED_RE = re.compile(
    r"(?:#|//|/\*|<!--)\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)(?:\*/|-->|$)",
    re.IGNORECASE,
)


def extract_todos_v2_combined(content: str) -> list[tuple[str, str, int]]:
    """Variation 2: Single combined regex."""
    todos = []
    for i, line in enumerate(content.splitlines(), 1):
        match = TODO_COMBINED_RE.search(line)
        if match:
            todos.append((match.group(1).upper(), match.group(2).strip(), i))
    return todos


def extract_todos_v3_findall(content: str) -> list[tuple[str, str, int]]:
    """Variation 3: findall on whole content then map to lines."""
    pattern = re.compile(
        r"^.*?(?:#|//|/\*|<!--)\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)(?:\*/|-->)?$",
        re.IGNORECASE | re.MULTILINE,
    )
    todos = []
    for match in pattern.finditer(content):
        line_num = content[: match.start()].count("\n") + 1
        todos.append((match.group(1).upper(), match.group(2).strip(), line_num))
    return todos


# ============================================================================
# BENCHMARKING FRAMEWORK
# ============================================================================


@dataclass
class BenchmarkResult:
    name: str
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    memory_estimate: str
    correctness: bool
    iterations: int


def benchmark_function(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    iterations: int = 100,
    warmup: int = 5,
) -> tuple[float, float, float]:
    """Benchmark a function, return (avg, min, max) times in ms."""
    # Warmup
    for _ in range(warmup):
        func(*args)

    times: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    return sum(times) / len(times), min(times), max(times)


def verify_correctness(
    funcs: list[Callable[..., Any]], args: tuple[Any, ...]
) -> list[bool]:
    """Verify all functions return equivalent results."""
    results = [func(*args) for func in funcs]
    baseline = results[0]

    def normalize(result: Any) -> Any:
        if isinstance(result, list):
            return sorted(str(x) for x in result)
        return result

    baseline_norm = normalize(baseline)
    return [normalize(r) == baseline_norm for r in results]


# ============================================================================
# TEST DATA GENERATION
# ============================================================================


def generate_test_prompt(complexity: str = "medium") -> str:
    """Generate test prompts of varying complexity."""
    if complexity == "simple":
        return "fix the bug in utils.py"
    elif complexity == "medium":
        return """
        Look at the hooks/*.py files and find any TODO comments.
        Also check src/**/*.ts for similar patterns.
        The function 'extract_patterns' might need optimization.
        """
    else:  # complex
        return """
        I need to refactor the entire hooks/ directory.
        Check *.py, *.ts, *.js, **/*.md files.
        Look for 'UserPromptSubmit' handler and 'hook_invocation' patterns.
        The path src/components/hooks/useAuth.tsx has issues.
        Also review config.json and package.json for dependencies.
        Find all instances of "deprecated" or "legacy" comments.
        """


def generate_test_file(lines: int = 1000) -> str:
    """Generate test file content with TODOs."""
    content_lines = []
    for i in range(lines):
        if i % 50 == 0:
            content_lines.append(f"# TODO: implement feature {i}")
        elif i % 75 == 0:
            content_lines.append(f"// FIXME: fix bug at line {i}")
        elif i % 100 == 0:
            content_lines.append(f"/* HACK: workaround for issue {i} */")
        else:
            content_lines.append(f"code_line_{i} = {i}")
    return "\n".join(content_lines)


def create_test_directory() -> Path:
    """Create a test directory with files."""
    tmpdir = Path(tempfile.mkdtemp())
    (tmpdir / "src").mkdir()
    (tmpdir / "hooks").mkdir()

    for name in ["utils.py", "main.py", "config.py"]:
        (tmpdir / name).write_text(generate_test_file(500))

    for name in ["hook1.py", "hook2.py"]:
        (tmpdir / "hooks" / name).write_text(generate_test_file(300))

    (tmpdir / "src" / "app.ts").write_text(generate_test_file(800))

    return tmpdir


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def run_permutation_tests() -> dict[str, list[BenchmarkResult]]:
    """Run all permutation tests and collect results."""
    results: dict[str, list[BenchmarkResult]] = {}

    # Test 1: Pattern extraction variations
    print("\n" + "=" * 60)
    print("TEST 1: Pattern Extraction Strategies")
    print("=" * 60)

    pattern_funcs = [
        ("v1_regex (original)", extract_patterns_v1_regex),
        ("v2_combined", extract_patterns_v2_combined),
        ("v3_precompiled", extract_patterns_v3_precompiled),
    ]

    for complexity in ["simple", "medium", "complex"]:
        prompt = generate_test_prompt(complexity)
        correctness = verify_correctness([f[1] for f in pattern_funcs], (prompt,))

        print(f"\n  Complexity: {complexity}")
        test_results = []
        for (name, func), correct in zip(pattern_funcs, correctness):
            avg, mn, mx = benchmark_function(func, (prompt,), iterations=1000)
            result = BenchmarkResult(
                name=name,
                avg_time_ms=avg,
                min_time_ms=mn,
                max_time_ms=mx,
                memory_estimate="low",
                correctness=correct,
                iterations=1000,
            )
            test_results.append(result)
            status = "PASS" if correct else "FAIL"
            print(f"    {name:25} avg={avg:.4f}ms  [{status}]")

        results[f"pattern_extraction_{complexity}"] = test_results

    # Test 2: File reading variations
    print("\n" + "=" * 60)
    print("TEST 2: File Reading Strategies")
    print("=" * 60)

    tmpdir = create_test_directory()
    read_funcs = [
        ("v1_readall (original)", head_tail_v1_readall),
        ("v2_streaming", head_tail_v2_streaming),
        ("v3_mmap", head_tail_v3_mmap),
    ]

    for size_name, lines in [("small", 100), ("medium", 1000), ("large", 5000)]:
        test_file = tmpdir / f"test_{size_name}.py"
        test_file.write_text(generate_test_file(lines))

        correctness = verify_correctness([f[1] for f in read_funcs], (test_file,))

        print(f"\n  File size: {size_name} ({lines} lines)")
        test_results = []
        for (name, func), correct in zip(read_funcs, correctness):
            avg, mn, mx = benchmark_function(func, (test_file,), iterations=100)
            mem = "high" if "readall" in name else "medium" if "mmap" in name else "low"
            result = BenchmarkResult(
                name=name,
                avg_time_ms=avg,
                min_time_ms=mn,
                max_time_ms=mx,
                memory_estimate=mem,
                correctness=correct,
                iterations=100,
            )
            test_results.append(result)
            status = "PASS" if correct else "FAIL"
            print(f"    {name:25} avg={avg:.4f}ms mem={mem:6} [{status}]")

        results[f"file_reading_{size_name}"] = test_results

    # Test 3: TODO extraction variations
    print("\n" + "=" * 60)
    print("TEST 3: TODO Extraction Strategies")
    print("=" * 60)

    todo_funcs = [
        ("v1_multipass (original)", extract_todos_v1_multipass),
        ("v2_combined", extract_todos_v2_combined),
        ("v3_findall", extract_todos_v3_findall),
    ]

    for size_name, lines in [("small", 100), ("medium", 1000), ("large", 5000)]:
        content = generate_test_file(lines)
        correctness = verify_correctness([f[1] for f in todo_funcs], (content,))

        print(f"\n  Content size: {size_name} ({lines} lines)")
        test_results = []
        for (name, func), correct in zip(todo_funcs, correctness):
            avg, mn, mx = benchmark_function(func, (content,), iterations=100)
            result = BenchmarkResult(
                name=name,
                avg_time_ms=avg,
                min_time_ms=mn,
                max_time_ms=mx,
                memory_estimate="medium",
                correctness=correct,
                iterations=100,
            )
            test_results.append(result)
            status = "PASS" if correct else "FAIL"
            print(f"    {name:25} avg={avg:.4f}ms  [{status}]")

        results[f"todo_extraction_{size_name}"] = test_results

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    return results


def generate_quality_report(results: dict[str, list[BenchmarkResult]]) -> str:
    """Generate quality gate evaluation report."""
    lines = [
        "",
        "=" * 70,
        "QUALITY GATE EVALUATION",
        "=" * 70,
        "",
    ]

    # Aggregate by function category
    categories = {
        "Pattern Extraction": [k for k in results if k.startswith("pattern")],
        "File Reading": [k for k in results if k.startswith("file")],
        "TODO Extraction": [k for k in results if k.startswith("todo")],
    }

    recommendations: list[tuple[str, str, str]] = []

    for category, test_keys in categories.items():
        lines.append(f"\n{category}:")
        lines.append("-" * 40)

        # Find best performer across all tests in category
        variant_scores: dict[str, list[float]] = {}
        for key in test_keys:
            for result in results[key]:
                if result.name not in variant_scores:
                    variant_scores[result.name] = []
                # Score: lower time is better, correctness is required
                score = result.avg_time_ms if result.correctness else 999
                variant_scores[result.name].append(score)

        # Calculate average scores
        avg_scores = {
            name: sum(scores) / len(scores) for name, scores in variant_scores.items()
        }
        ranked = sorted(avg_scores.items(), key=lambda x: x[1])

        for i, (name, score) in enumerate(ranked):
            marker = " RECOMMENDED" if i == 0 else ""
            lines.append(f"  {i+1}. {name:30} avg={score:.4f}ms{marker}")

        # Add recommendation
        if ranked:
            best_name = ranked[0][0]
            original = next((n for n, _ in ranked if "original" in n), None)
            if original and original != best_name:
                improvement = (
                    (avg_scores[original] - avg_scores[best_name])
                    / avg_scores[original]
                    * 100
                )
                recommendations.append(
                    (
                        category,
                        best_name,
                        f"{improvement:.1f}% faster than original",
                    )
                )
            else:
                recommendations.append((category, best_name, "current implementation optimal"))

    # Summary
    lines.append("\n" + "=" * 70)
    lines.append("RECOMMENDATIONS")
    lines.append("=" * 70)

    for category, variant, reason in recommendations:
        lines.append(f"\n{category}:")
        lines.append(f"  Use: {variant}")
        lines.append(f"  Reason: {reason}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Code Permutation Testing")
    print("Hooks: jit_context.py, todo_tracker.py")
    print("=" * 60)

    results = run_permutation_tests()
    report = generate_quality_report(results)
    print(report)
