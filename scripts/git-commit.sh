#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [ -z "$1" ]; then
    echo "Usage: git-commit.sh 'commit message'"
    exit 1
fi

echo "=== GIT COMMIT ==="
echo "Staging changes..."
git add -A

echo "Committing with message: '$1'"
git commit -m "$1"

echo "✓ Commit created"
git log --oneline -1
