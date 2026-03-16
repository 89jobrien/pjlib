---
paths: "**/*.sh"
---

# Shell Script Rules

## Header

**Always include shebang and set options:**

```bash
#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

## Style Guide

### Variable Naming

```bash
# Good
local user_name="alice"          # Local variables: snake_case
readonly MAX_RETRIES=3            # Constants: UPPER_CASE
export DATABASE_URL="..."         # Environment: UPPER_CASE

# Bad
USERNAME="alice"                  # Looks like env var
local MaxRetries=3                # Not shell convention
```

### Quoting

**Always quote variables:**

```bash
# Good
echo "$user_name"
ls -la "$directory"
command --arg="$value"

# Bad
echo $user_name          # Word splitting issues
ls -la $directory        # Breaks with spaces
command --arg=$value     # Unsafe
```

### Conditionals

**Use `[[ ]]` for tests:**

```bash
# Good
if [[ -f "$file" ]]; then
    echo "File exists"
fi

if [[ "$status" == "active" ]]; then
    echo "Status is active"
fi

# Bad
if [ -f $file ]         # Use [[ ]] instead
if test -f $file        # Use [[ ]] instead
```

### Functions

```bash
# Good - clear function definition
function process_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi

    # Process file
    cat "$file" | grep "pattern"
}

# Call with
process_file "data.txt"
```

## Error Handling

**Check exit codes and fail fast:**

```bash
#!/usr/bin/env bash
set -euo pipefail  # Exit on any error

# Check command success
if ! command -v uv &>/dev/null; then
    echo "Error: uv not found" >&2
    exit 1
fi

# Capture and check
output=$(some_command) || {
    echo "Command failed" >&2
    exit 1
}

# Conditional execution
command || echo "Warning: command failed" >&2
```

## Common Patterns

### Argument Parsing

```bash
#!/usr/bin/env bash
set -euo pipefail

function show_usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] FILE

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose output
    -o, --output    Output file
EOF
}

verbose=false
output_file=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            verbose=true
            shift
            ;;
        -o|--output)
            output_file="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            show_usage
            exit 1
            ;;
    esac
done
```

### Temporary Files

```bash
# Create temp file/directory
temp_file=$(mktemp)
temp_dir=$(mktemp -d)

# Cleanup on exit
trap "rm -rf $temp_file $temp_dir" EXIT

# Use temp file
echo "data" > "$temp_file"
```

### Loops

```bash
# Iterate over files
for file in *.txt; do
    echo "Processing: $file"
    process_file "$file"
done

# Read lines from file
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt

# Command output
while IFS= read -r line; do
    echo "$line"
done < <(find . -name "*.py")
```

### Colors (Optional)

```bash
# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo -e "${GREEN}Success${NC}"
echo -e "${RED}Error${NC}"
echo -e "${YELLOW}Warning${NC}"
```

## Tool Integration

### Python Commands

**Remember: No vanilla Python on PATH!**

```bash
# Good
uv run pytest tests/
uv run python script.py
uv run -m module

# Bad
python script.py          # Won't work
pip install package       # Use uv add
```

### TypeScript Commands

**Use bun:**

```bash
# Good
bun script.ts
bun test
bunx tsc --noEmit

# Bad
node script.js            # Use bun
npm install               # Use bun install
npx tool                  # Use bunx
```

### Git Operations

```bash
# Check if in git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "Not a git repository" >&2
    exit 1
fi

# Get repo root
repo_root=$(git rev-parse --show-toplevel)

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Uncommitted changes detected" >&2
    exit 1
fi
```

## Best Practices

### Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Script description
# Usage: script.sh [OPTIONS]

# Global variables
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# Functions
function log_info() {
    echo "[INFO] $*" >&2
}

function log_error() {
    echo "[ERROR] $*" >&2
}

function cleanup() {
    log_info "Cleaning up..."
    # Cleanup logic
}

# Cleanup on exit
trap cleanup EXIT

# Main logic
function main() {
    log_info "Starting $SCRIPT_NAME"

    # Script logic here

    log_info "Completed successfully"
}

# Run main
main "$@"
```

### Checking Dependencies

```bash
function check_dependencies() {
    local missing=()

    for cmd in uv bun git; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing dependencies: ${missing[*]}" >&2
        exit 1
    fi
}

check_dependencies
```

## Common Mistakes to Avoid

### Don't

```bash
# Bad - unquoted variables
cd $directory        # Breaks with spaces
rm -rf $temp_dir/*   # Dangerous

# Bad - unnecessary subshell
result=`command`     # Use $() instead

# Bad - unsafe conditions
if [ $status = "ok" ]  # Use [[ ]] instead

# Bad - bare commands
python script.py       # No python on PATH!
npm install           # Use bun install
```

### Do

```bash
# Good - quoted and safe
cd "$directory"
rm -rf "${temp_dir:?}/"

# Good - modern syntax
result=$(command)

# Good - safe conditions
if [[ "$status" == "ok" ]]; then

# Good - correct tools
uv run script.py
bun install
```

## ShellCheck

**Always run shellcheck on scripts:**

```bash
# Install
brew install shellcheck  # macOS
apt-get install shellcheck  # Ubuntu

# Run
shellcheck script.sh

# In pre-commit hook
shellcheck --severity=warning script.sh
```
