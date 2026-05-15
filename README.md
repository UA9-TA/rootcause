# RootCause

<p align="center">
  <strong>AI-powered root cause analysis for failing tests and runtime errors.</strong><br>
  Point it at any failure. Get the exact fix.
</p>

<p align="center">
  <a href="https://github.com/UA9-TA/rootcause/actions/workflows/ci.yml"><img src="https://github.com/UA9-TA/rootcause/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/rootcause/"><img src="https://img.shields.io/pypi/v/rootcause.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/rootcause/"><img src="https://img.shields.io/pypi/pyversions/rootcause.svg" alt="Python versions"></a>
  <a href="https://github.com/UA9-TA/rootcause/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

---

<!-- demo.gif — record with: asciinema rec demo.cast && agg demo.cast demo.gif -->

## What It Does

RootCause runs your failing test, instruments the execution, gathers source code context and recent git changes, then asks Claude to pinpoint the **exact** root cause and write the fix.

This is not "ask ChatGPT about your error." ChatGPT sees what you paste. RootCause sees:
- The full stack trace with every frame
- ±30 lines of source around each failure location
- The last 5 git commits touching those files
- Your Python version, OS, and package versions
- Live execution traces via `sys.settrace`

All of that flows into a structured Claude prompt that returns a precise, actionable fix.

## Install

```bash
pip install rootcause
```

## Quick Start

```bash
# Set your API key once
rootcause config sk-ant-...

# Analyze a failing pytest test
rootcause pytest tests/test_auth.py::test_login

# Analyze a raw error log
rootcause analyze error.log

# Analyze the last error in your terminal
rootcause last
```

## Example Output

```
╭─ RootCause Analysis ──────────────────────────────────────────────────────╮
│                                                                            │
│  Root cause    JWT token comparison fails on non-UTC systems               │
│  Location      auth/validators.py:147                                      │
│                                                                            │
│  Explanation   datetime.now() returns local time but the JWT exp field     │
│                is UTC. On IST/PST systems this causes all tokens to        │
│                appear expired immediately. The delta is your UTC offset.   │
│                                                                            │
│  Fix           Replace datetime.now() with datetime.utcnow()               │
│                or timezone-aware: datetime.now(timezone.utc)               │
│                                                                            │
│  Also found    Same pattern at session.py:89 — likely the same bug         │
│                                                                            │
│  Confidence    94%                                                         │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯
Apply fix automatically? [y/N]
```

## How It Works

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────┐
│  Run Test   │───▶│  Capture Trace   │───▶│   Gather Context    │───▶│  AI Analysis │
│             │    │                  │    │                     │    │              │
│ pytest/jest │    │ sys.settrace     │    │ Source ±30 lines    │    │ Claude       │
│ mocha/log   │    │ stdout + stderr  │    │ Git diff (5 commits)│    │ Sonnet 4.6   │
│             │    │ exit code        │    │ Python env info     │    │              │
└─────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────┘
```

## Real Example

**The bug:** A JWT auth test passes on UTC servers but fails on IST/PST machines.

```python
# tests/test_auth.py — this fails on non-UTC systems
def test_token_expiration():
    token = create_jwt(expires_in=300)  # 5 minutes
    assert is_valid(token)              # AssertionError on IST/PST
```

**Run RootCause:**
```bash
rootcause pytest tests/test_auth.py::test_token_expiration
```

**What it finds:** Points directly to `auth/validators.py:147` where `datetime.now()` is compared against a UTC timestamp. Gives you the one-line fix. Spots the same pattern in `session.py:89` before you even knew it was there.

## Supported Frameworks

| Framework | Status | Command |
|-----------|--------|---------|
| pytest | ✅ Supported | `rootcause pytest tests/test_x.py::test_fn` |
| jest | ✅ Supported | `rootcause jest src/__tests__/auth.test.js` |
| mocha | ✅ Supported | `rootcause jest test/auth.spec.js` |
| error logs | ✅ Supported | `rootcause analyze error.log` |
| rspec | 🔜 Soon | — |
| go test | 🔜 Soon | — |

## Configuration

```bash
# Option 1: environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Option 2: save permanently
rootcause config sk-ant-...
# Stored in ~/.rootcause/config.toml
```

## Why Not Just Ask ChatGPT?

| | ChatGPT / manual | RootCause |
|---|---|---|
| Context | What you paste | Full execution trace + source + git |
| Accuracy | Guesses at missing code | Reads the actual files |
| Speed | 5–10 mins of copy-paste | One command |
| Related bugs | You have to find them | Scans for related patterns |
| Fix format | Prose suggestion | Unified diff, apply with one keystroke |

When you paste an error into ChatGPT, you're hoping you copied the right lines. RootCause knows exactly which lines ran, in what order — because it watched the execution happen.

## Auto-Fix

When RootCause is confident (>80%), it generates a unified diff you can apply instantly:

```bash
rootcause pytest tests/test_auth.py::test_login --auto-fix
```

Or interactively — RootCause shows the diff and asks for confirmation before touching any file.

## Contributing

```bash
git clone https://github.com/UA9-TA/rootcause.git
cd rootcause
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

PRs welcome. Open an issue first for large changes.


## The Developer Toolkit Ecosystem

RootCause is part of a suite of open-source AI-powered developer tools:

| Tool | What it does |
|---|---|
| **[RootCause](https://github.com/UA9-TA/rootcause)** | Auto-diagnose failing tests — AI root cause + fix |
| **[ErrorMentor](https://github.com/UA9-TA/errormentor)** | Auto-diagnose production errors — correlate logs with git commits |
| **[TestGap](https://github.com/UA9-TA/testgap)** | Find untested code paths after every commit |
| **[HalluCheck](https://github.com/UA9-TA/hallucheck)** | Catch AI hallucinations in code diffs |
| **[IntentDiff](https://github.com/UA9-TA/intentdiff)** | Understand what a diff *actually* does semantically |
| **[DepSecure](https://github.com/UA9-TA/depsecure)** | Block vulnerable dependencies at commit time |
| **[ArchGuard](https://github.com/UA9-TA/archguard)** | Enforce microservice architecture rules across repos |
| **[SpendSentry](https://github.com/UA9-TA/spendsentry)** | Monitor cloud spend in real time — alert before costs spiral |
| **[ContextKit](https://github.com/UA9-TA/contextkit)** | Build minimal AI context bundles — 88% fewer tokens |

## License

MIT
