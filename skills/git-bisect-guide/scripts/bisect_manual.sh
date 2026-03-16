#!/bin/bash
# bisect_manual.sh - Guided manual bisect

git bisect start
git bisect bad HEAD
git bisect good v1.2.0

while true; do
    # Show current commit
    echo "=== Testing Commit ==="
    git log -1 --oneline
    git show --stat --pretty=""

    # Wait for user input
    echo ""
    echo "Test this commit, then enter:"
    echo "  g = good"
    echo "  b = bad"
    echo "  s = skip (cannot determine)"
    echo "  q = quit"
    read -p "> " choice

    case "$choice" in
        g) git bisect good || break ;;
        b) git bisect bad || break ;;
        s) git bisect skip || break ;;
        q) git bisect reset; exit 0 ;;
        *) echo "Invalid choice" ;;
    esac
done

# Show results
git bisect log
git bisect reset
