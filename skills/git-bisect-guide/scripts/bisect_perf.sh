#!/bin/bash
# bisect_perf.sh - Performance bisect

# Threshold: 100ms
THRESHOLD_MS=100

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

git bisect run bash -c '
    cargo build --release --quiet || exit 125

    # Run benchmark 3 times, take average
    total=0
    for i in 1 2 3; do
        time_ms=$(cargo bench --bench perf | grep -oE "[0-9]+ ms" | grep -oE "[0-9]+")
        total=$((total + time_ms))
    done
    avg=$((total / 3))

    echo "Average time: ${avg}ms (threshold: '"$THRESHOLD_MS"'ms)"

    if [ $avg -gt '"$THRESHOLD_MS"' ]; then
        exit 1  # Bad (slow)
    else
        exit 0  # Good (fast)
    fi
'

git bisect log
git bisect reset
