#!/bin/bash
# bisect_auto.sh - Automatic bisect script

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

# Run bisect with test command
git bisect run cargo test --test auth_regression

# Capture result
RESULT=$?

# Cleanup and report
git bisect log > bisect-results.log
git bisect reset

echo "Bisect complete. Results in bisect-results.log"
exit $RESULT
