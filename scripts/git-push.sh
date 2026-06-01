#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "=== GIT PUSH ==="
echo "Pushing to GitHub..."

git push origin main

echo "✓ Push complete"
git log --oneline -1
