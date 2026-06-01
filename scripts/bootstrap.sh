#!/bin/bash
set -e

AIOS_HOME="$HOME/.venvs/aios"
AIOS_PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== AIOS BOOTSTRAP ==="
echo "Project: $AIOS_PROJECT"
echo "Runtime: $AIOS_HOME"
echo

# 1. Verify venv exists
if [ ! -d "$AIOS_HOME" ]; then
    echo "Creating virtual environment..."
    uv venv "$AIOS_HOME" --python 3.13
fi

# 2. Activate venv
source "$AIOS_HOME/bin/activate"
echo "✓ Virtual environment activated"

# 3. Verify dependencies
echo "Verifying dependencies..."
uv pip sync "$AIOS_PROJECT/pyproject.toml" > /dev/null 2>&1
echo "✓ Dependencies verified"

# 4. Verify git
if ! git -C "$AIOS_PROJECT" status > /dev/null 2>&1; then
    echo "✗ Git repository not initialized"
    exit 1
fi
echo "✓ Git repository healthy"

# 5. Check GitHub remote
if ! git -C "$AIOS_PROJECT" remote -v | grep -q "origin"; then
    echo "✗ GitHub remote not configured"
    exit 1
fi
echo "✓ GitHub remote configured"

echo
echo "=== BOOTSTRAP COMPLETE ==="
echo "Run: source activate.sh"
echo "Or: source $AIOS_HOME/bin/activate"
