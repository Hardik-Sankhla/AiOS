"""PHASE 5 STEP 1: Repository Audit - Identify structure, dead code, duplicates."""

import os
import sys
from pathlib import Path
from collections import defaultdict

def count_lines(filepath):
    """Count lines in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def analyze_repo():
    """Analyze repository structure."""
    root = Path('/storage/emulated/0/projects/aios')
    
    print("📊 REPOSITORY STRUCTURE ANALYSIS")
    print("=" * 70)
    
    # Collect modules
    modules = defaultdict(list)
    total_lines = 0
    file_count = 0
    
    # Ignore patterns
    ignore_dirs = {'.git', '.venv', '__pycache__', 'site', '.pytest_cache', '.mypy_cache'}
    ignore_files = {'.pyc', '.pyo', '.pyd', '.so', '.egg-info'}
    
    for py_file in root.rglob('*.py'):
        # Skip ignored dirs
        if any(part in ignore_dirs for part in py_file.parts):
            continue
        
        rel_path = py_file.relative_to(root)
        category = rel_path.parts[0] if rel_path.parts else 'root'
        
        lines = count_lines(py_file)
        modules[category].append({
            'path': str(rel_path),
            'lines': lines
        })
        total_lines += lines
        file_count += 1
    
    # Print by category
    print("\n📁 MODULES BY CATEGORY:\n")
    for category in sorted(modules.keys()):
        files = modules[category]
        category_lines = sum(f['lines'] for f in files)
        print(f"{category}/ ({category_lines} lines, {len(files)} files)")
        for f in sorted(files, key=lambda x: x['lines'], reverse=True):
            print(f"  ├─ {f['path']:<40} {f['lines']:>4} lines")
    
    print(f"\n{'='*70}")
    print(f"📈 TOTALS: {file_count} files, {total_lines:,} lines of Python code")
    
    # List all directories
    print(f"\n📂 DIRECTORY TREE:\n")
    for d in sorted(root.glob('*')):
        if d.is_dir() and not d.name.startswith('.'):
            py_count = len(list(d.glob('**/*.py')))
            if py_count > 0 or d.name in ['webui', 'scripts', 'configs']:
                status = f"({py_count} .py files)" if py_count > 0 else "(empty)"
                print(f"  {d.name}/ {status}")

analyze_repo()
