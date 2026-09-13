# File Integrity Monitoring (FIM) Tool

A simple, from-scratch File Integrity Monitoring tool written in Python. It creates a baseline snapshot of a directory's files and lets you check that directory later to detect any files that were added, removed, or modified.

> **Version 1.0** — a first working version, with room to grow. See [Planned improvements](#planned-improvements) for what's next.

## How it works

1. **Baseline** — the tool scans a target directory and computes a SHA-256 hash for every file inside it, then saves those hashes to a JSON file.
2. **Check** — the tool re-scans the same directory, recomputes the hashes, and compares them against the saved baseline.
3. Any differences are reported as:
   - **Added** — files present now that weren't in the baseline
   - **Removed** — files that were in the baseline but no longer exist
   - **Modified** — files that exist in both but whose contents have changed

## Requirements

- Python 3.x (no external libraries required — uses only the standard library: `hashlib`, `os`, `json`, `argparse`, `datetime`)

## Usage

Create a baseline of a directory:
```
python fmi.py baseline <directory>
```

Check a directory against its saved baseline:
```
python fmi.py check <directory>
```

### Example

```
python fmi.py baseline "C:/Users/you/Desktop/projects/test_target"
python fmi.py check "C:/Users/you/Desktop/projects/test_target"
```

## Functionality

- Recursively scans all files within a target directory
- Computes SHA-256 hashes for reliable, byte-for-byte change detection
- Stores baselines as human-readable JSON
- Detects and clearly reports added, removed, and modified files
- Handles unreadable files (e.g. permission errors) gracefully instead of crashing
- Command-line interface with `baseline` and `check` subcommands

## Planned improvements

This is version 1 — a working core with room to grow. Planned for future versions:
- Logging every baseline/check run with timestamps to a persistent log file
- An interactive CLI menu instead of typing commands manually each time
- File/extension exclusion support
- Config file support for default settings (e.g. default target directory)
- Real-time monitoring using filesystem events instead of manual checks
- Alerting (e.g. email or webhook notifications) when changes are detected
