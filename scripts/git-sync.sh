#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "=== GIT SYNC ==="

echo "Fetching from GitHub..."
git fetch origin main

echo "Pulling latest changes..."
git pull origin main

echo "✓ Sync complete"
git status
