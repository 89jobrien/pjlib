#!/usr/bin/env python3
"""
Aggregate test results into benchmark report.
Usage: python aggregate_benchmark.py --workspace iteration-1 --configs baseline treatment --test-name my-test
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import Dict, List


def load_timing(path: Path) -> Dict:
    """Load timing data from timing.json."""
    with open(path) as f:
        return json.load(f)


def load_grading(path: Path) -> Dict:
    """Load grading data from grading.json."""
    with open(path) as f:
        return json.load(f)


def calculate_pass_rate(grading: Dict) -> float:
    """Calculate pass rate from grading data."""
    expectations = grading.get('expectations', [])
    if not expectations:
        return 0.0
    passed = sum(1 for exp in expectations if exp.get('passed', False))
    return passed / len(expectations)


def aggregate_config(workspace: Path, config: str, test_cases: List[Path]) -> Dict:
    """Aggregate metrics for a single configuration across all test cases."""
    pass_rates = []
    tokens = []
    times = []

    for test_case_dir in test_cases:
        config_dir = test_case_dir / config

        # Load and aggregate grading
        grading_file = config_dir / 'grading.json'
        if grading_file.exists():
            grading = load_grading(grading_file)
            pass_rates.append(calculate_pass_rate(grading))

        # Load and aggregate timing
        timing_file = config_dir / 'timing.json'
        if timing_file.exists():
            timing = load_timing(timing_file)
            tokens.append(timing['total_tokens'])
            times.append(timing['total_duration_seconds'])

    return {
        'pass_rate': {
            'mean': statistics.mean(pass_rates) if pass_rates else 0.0,
            'values': pass_rates
        },
        'tokens': {
            'mean': statistics.mean(tokens) if tokens else 0,
            'stddev': statistics.stdev(tokens) if len(tokens) > 1 else 0,
            'values': tokens
        },
        'time_seconds': {
            'mean': statistics.mean(times) if times else 0,
            'stddev': statistics.stdev(times) if len(times) > 1 else 0,
            'values': times
        }
    }


def find_test_cases(workspace: Path) -> List[Path]:
    """Find all test case directories in workspace."""
    test_cases = []
    for item in workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Check if it has config subdirectories
            has_configs = any(
                (item / d).is_dir()
                for d in ['baseline', 'treatment']
            )
            if has_configs:
                test_cases.append(item)
    return sorted(test_cases)


def generate_markdown_report(benchmark: Dict, test_name: str) -> str:
    """Generate human-readable markdown report."""
    configs = benchmark['configurations']
    baseline = next((c for c in configs if 'baseline' in c['name'].lower()), configs[0])
    treatments = [c for c in configs if c != baseline]

    report = [f"# {test_name} - Benchmark Results\n"]
    report.append(f"**Test Cases:** {len(baseline['pass_rate']['values'])}")
    report.append(f"**Configurations:** {len(configs)}\n")

    report.append("## Results\n")

    # Pass Rate
    report.append("### Pass Rate")
    report.append(f"- **{baseline['name']}:** {baseline['pass_rate']['mean']:.1%}")
    for treatment in treatments:
        delta = treatment['pass_rate']['mean'] - baseline['pass_rate']['mean']
        report.append(f"- **{treatment['name']}:** {treatment['pass_rate']['mean']:.1%} (delta: {delta:+.1%})")
    report.append("")

    # Token Usage
    report.append("### Token Usage")
    report.append(
        f"- **{baseline['name']}:** {baseline['tokens']['mean']:.0f} ± {baseline['tokens']['stddev']:.0f}"
    )
    for treatment in treatments:
        delta = treatment['tokens']['mean'] - baseline['tokens']['mean']
        pct = (delta / baseline['tokens']['mean'] * 100) if baseline['tokens']['mean'] > 0 else 0
        report.append(
            f"- **{treatment['name']}:** {treatment['tokens']['mean']:.0f} ± {treatment['tokens']['stddev']:.0f} "
            f"(delta: {delta:+.0f}, {pct:+.1f}%)"
        )
    report.append("")

    # Execution Time
    report.append("### Execution Time")
    report.append(
        f"- **{baseline['name']}:** {baseline['time_seconds']['mean']:.1f} ± {baseline['time_seconds']['stddev']:.1f}s"
    )
    for treatment in treatments:
        delta = treatment['time_seconds']['mean'] - baseline['time_seconds']['mean']
        pct = (delta / baseline['time_seconds']['mean'] * 100) if baseline['time_seconds']['mean'] > 0 else 0
        report.append(
            f"- **{treatment['name']}:** {treatment['time_seconds']['mean']:.1f} ± {treatment['time_seconds']['stddev']:.1f}s "
            f"(delta: {delta:+.1f}s, {pct:+.1f}%)"
        )
    report.append("")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Aggregate benchmark results")
    parser.add_argument('--workspace', type=Path, required=True, help="Workspace directory (e.g., iteration-1)")
    parser.add_argument('--configs', nargs='+', required=True, help="Configuration names (e.g., baseline treatment)")
    parser.add_argument('--test-name', required=True, help="Name of test")

    args = parser.parse_args()

    if not args.workspace.exists():
        print(f"Error: Workspace {args.workspace} does not exist")
        return 1

    # Find test cases
    test_cases = find_test_cases(args.workspace)
    if not test_cases:
        print(f"Error: No test cases found in {args.workspace}")
        return 1

    print(f"Found {len(test_cases)} test cases: {[tc.name for tc in test_cases]}")

    # Aggregate each configuration
    configurations = []
    for config in args.configs:
        print(f"Aggregating {config}...")
        config_data = aggregate_config(args.workspace, config, test_cases)
        config_data['name'] = config
        configurations.append(config_data)

    # Create benchmark
    benchmark = {
        'test_name': args.test_name,
        'test_cases': [tc.name for tc in test_cases],
        'configurations': configurations
    }

    # Calculate deltas (vs first config, assumed to be baseline)
    if len(configurations) > 1:
        baseline = configurations[0]
        deltas = []
        for treatment in configurations[1:]:
            deltas.append({
                'config': treatment['name'],
                'pass_rate': treatment['pass_rate']['mean'] - baseline['pass_rate']['mean'],
                'tokens': treatment['tokens']['mean'] - baseline['tokens']['mean'],
                'time_seconds': treatment['time_seconds']['mean'] - baseline['time_seconds']['mean']
            })
        benchmark['deltas'] = deltas

    # Save benchmark.json
    benchmark_json = args.workspace / 'benchmark.json'
    with open(benchmark_json, 'w') as f:
        json.dump(benchmark, f, indent=2)
    print(f"Saved benchmark.json to {benchmark_json}")

    # Generate markdown report
    report = generate_markdown_report(benchmark, args.test_name)
    benchmark_md = args.workspace / 'benchmark.md'
    with open(benchmark_md, 'w') as f:
        f.write(report)
    print(f"Saved benchmark.md to {benchmark_md}")

    print("\nBenchmark generated successfully!")
    return 0


if __name__ == '__main__':
    exit(main())
