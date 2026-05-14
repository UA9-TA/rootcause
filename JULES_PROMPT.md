# Jules Build Prompt — RootCause v1.0

## What You Are Building

**RootCause** is an open-source CLI tool that performs AI-powered root cause analysis on failing tests and runtime errors. A developer runs one command pointing at a failing test or error log — RootCause instruments the code, captures the full execution trace, and returns the exact root cause + fix in plain English.

This is not "ask ChatGPT about your code." This is systematic, automated debugging: trace collection → context gathering → AI analysis → actionable fix.

**Target:** Top GitHub trending repo. README must be exceptional. Demo must be undeniable.

---

## Core User Flow

```bash
# Install
pip install rootcause

# Use — point at a failing pytest test
rootcause pytest tests/test_auth.py::test_login

# Use — point at a failing jest test
rootcause jest src/__tests__/auth.test.js

# Use — analyze a raw traceback/error log
rootcause analyze error.log

# Use — analyze last terminal error
rootcause last
```

**Output:**
```
RootCause Analysis
──────────────────────────────────────────────────
✦ Root cause     JWT token comparison fails on non-UTC systems
✦ Location       auth/validators.py:147
✦ Explanation    datetime.now() returns local time but the JWT
                 exp field is UTC. On IST/PST systems this causes
                 all tokens to appear expired immediately.
✦ Fix            Replace datetime.now() with datetime.utcnow()
                 or use timezone-aware: datetime.now(timezone.utc)
✦ Also found     Same pattern at session.py:89 — likely same bug
✦ Confidence     94%
──────────────────────────────────────────────────
Apply fix automatically? [y/N]
```

---

## Tech Stack

- **Language:** Python 3.10+
- **CLI framework:** Typer + Rich (beautiful terminal output, colors, spinners)
- **AI:** Anthropic Claude API (`claude-sonnet-4-6`) via `anthropic` Python SDK
- **Test runner integration:** subprocess + output parsing
- **Code instrumentation:** `sys.settrace` for Python, subprocess stderr capture for JS
- **Packaging:** pyproject.toml (hatchling), published to PyPI as `rootcause`
- **Config:** `~/.rootcause/config.toml` for API key storage

---

## Project Structure

```
rootcause/
├── rootcause/
│   ├── __init__.py
│   ├── cli.py              # Typer app — all commands defined here
│   ├── runner.py           # Runs test commands, captures stdout/stderr/exit code
│   ├── tracer.py           # Python sys.settrace instrumentation
│   ├── context.py          # Gathers relevant source code around the failure
│   ├── analyzer.py         # Sends context to Claude API, parses response
│   ├── patcher.py          # Optional: applies the suggested fix to source files
│   ├── display.py          # Rich-based terminal output formatting
│   └── config.py           # Reads/writes ~/.rootcause/config.toml
├── tests/
│   ├── test_runner.py
│   ├── test_context.py
│   ├── test_analyzer.py
│   └── fixtures/
│       ├── sample_failing_test.py    # A real broken test for demo
│       └── sample_error.log          # A real error log for demo
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions: test on push
├── pyproject.toml
├── README.md               # CRITICAL — see README spec below
└── JULES_PROMPT.md         # This file
```

---

## Detailed Module Specs

### `cli.py` — Entry point
```python
app = typer.Typer(name="rootcause", help="AI-powered root cause analysis for failing tests")

@app.command()
def pytest_cmd(test_path: str, auto_fix: bool = False):
    """Analyze a failing pytest test."""

@app.command()  
def jest_cmd(test_path: str, auto_fix: bool = False):
    """Analyze a failing jest test."""

@app.command()
def analyze(file: str):
    """Analyze a raw error log or traceback file."""

@app.command()
def last():
    """Analyze the last error in terminal history."""

@app.command()
def config(api_key: str):
    """Set your Anthropic API key."""
```

### `runner.py` — Test execution
- Run the test command as subprocess
- Capture: stdout, stderr, exit code, runtime
- Detect test framework from command (pytest/jest/mocha/rspec)
- Parse the failure output to extract: test name, error type, traceback, line numbers
- Return structured `FailureReport` dataclass

### `context.py` — Code context gathering
Given a traceback with file paths + line numbers:
1. Read each referenced source file
2. Extract ±30 lines around each error location
3. Find the test function body
4. Find the function under test (if identifiable from imports)
5. Check git diff (last 5 commits) for recent changes to failing files
6. Return all context as a structured string, token-budget-aware (max 8000 tokens)

### `analyzer.py` — Claude API integration
Build a precise prompt with:
- The failure output (stderr/stdout)
- The parsed traceback
- The source code context
- Recent git changes
- System info (Python version, OS, key package versions)

Send to `claude-sonnet-4-6`. Parse the response into:
```python
@dataclass
class Analysis:
    root_cause: str        # One sentence
    location: str          # file:line
    explanation: str       # 2-4 sentences, plain English
    fix: str               # Exact code change
    also_found: list[str]  # Other related issues spotted
    confidence: int        # 0-100
    fix_diff: str          # Optional: actual unified diff to apply
```

**Prompt engineering is critical.** The Claude prompt must instruct it to:
- Return structured JSON (easier to parse)
- Be specific about file and line numbers
- Explain in plain English why it failed
- Not hallucinate files/lines that don't exist
- Always give a concrete fix, not vague suggestions

### `display.py` — Rich terminal UI
Use Rich panels, colored text, and icons. The output should look exceptional:
- Spinner while analyzing ("Tracing execution...", "Gathering context...", "Analyzing with AI...")
- Clear section headers
- Root cause in bold
- Code snippets with syntax highlighting
- Confidence as a colored percentage (green >80%, yellow 60-80%, red <60%)

### `patcher.py` — Auto-fix (optional, only with --auto-fix flag)
- Parse the fix_diff from the analysis
- Show the diff to user with Rich
- Ask for confirmation
- Apply the patch using Python's `difflib` or write directly
- Run the test again to verify the fix worked

---

## The Claude Prompt Template

```
You are an expert debugging assistant performing root cause analysis.

A developer's test is failing. Analyze the failure and identify the EXACT root cause.

## Failing Test Output
{failure_output}

## Source Code Context
{source_context}

## Recent Git Changes (last 5 commits touching these files)
{git_context}

## Environment
{env_info}

Respond with ONLY valid JSON in this exact format:
{
  "root_cause": "One sentence describing the exact root cause",
  "location": "filename.py:line_number",
  "explanation": "2-4 sentences explaining WHY this causes the failure",
  "fix": "Exact code change needed — show before and after",
  "also_found": ["list of other potential issues spotted, or empty array"],
  "confidence": 87,
  "fix_diff": "unified diff format if applicable, or null"
}

Rules:
- Only reference files and line numbers that appear in the context above
- Be specific — generic answers like 'check your configuration' are not acceptable
- confidence should reflect how certain you are (not how hard the fix is)
- If you cannot determine root cause, set confidence below 40 and explain why
```

---

## README Spec (CRITICAL for GitHub stars)

The README is what gets the repo starred. It must be world-class.

### Structure:
1. **Hero banner** — ASCII art or badge-heavy header
2. **One-liner** — "Point it at any failing test. Get the exact fix."
3. **Demo GIF** — (placeholder comment: `<!-- Add demo.gif here -->`)
4. **Install** — `pip install rootcause` — nothing else
5. **Quick start** — 3 commands, real output shown with Rich-formatted code block
6. **How it works** — Simple 4-step diagram in ASCII
7. **Supported frameworks** — Table: pytest ✅ jest ✅ mocha ✅ rspec 🔜 go test 🔜
8. **Configuration** — Just the API key setup
9. **Why not just ask ChatGPT?** — Explain the difference (systematic trace collection + code context vs copy-paste)
10. **Contributing** — Simple guide
11. **License** — MIT

### The README must make someone want to star it before they even try it.

---

## GitHub Actions CI (`ci.yml`)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v
      - run: ruff check rootcause/
```

---

## `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "rootcause"
version = "0.1.0"
description = "AI-powered root cause analysis for failing tests and errors"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["debugging", "testing", "ai", "developer-tools", "cli"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Topic :: Software Development :: Debuggers",
    "Topic :: Software Development :: Testing",
]
dependencies = [
    "typer>=0.12",
    "rich>=13",
    "anthropic>=0.25",
    "tomli>=2.0; python_version < '3.11'",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "pytest-mock"]

[project.scripts]
rootcause = "rootcause.cli:app"

[project.urls]
Homepage = "https://github.com/UA9-TA/rootcause"
Repository = "https://github.com/UA9-TA/rootcause"
Issues = "https://github.com/UA9-TA/rootcause/issues"
```

---

## Sample Fixture Files (must be real, working examples)

### `tests/fixtures/sample_failing_test.py`
A real Python test that fails due to a timezone/datetime bug (the classic example from the README demo). This test should:
1. Actually fail when run with pytest
2. Produce a realistic, non-trivial traceback
3. Be the exact example used in the README demo

### `tests/fixtures/sample_error.log`
A realistic production error log (500 lines, multiple services, one root cause buried inside).

---

## What NOT to Build in v1

- No web UI or dashboard
- No database or persistence
- No team/sharing features
- No support for compiled languages (C, Java, Go) — Python + JS only in v1
- No IDE extension — CLI only
- No automatic PyPI publish — just the code

---

## Definition of Done

- [ ] `pip install rootcause` works (local install with `pip install -e .`)
- [ ] `rootcause pytest tests/fixtures/sample_failing_test.py` produces correct analysis
- [ ] `rootcause analyze tests/fixtures/sample_error.log` produces correct analysis
- [ ] `rootcause config <key>` stores API key in `~/.rootcause/config.toml`
- [ ] All output uses Rich for beautiful formatting (no raw print statements)
- [ ] All modules have tests with >70% coverage
- [ ] README is complete, compelling, and copy-paste ready
- [ ] CI passes on GitHub
- [ ] Code passes `ruff` linting

---

## Environment Variable

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# OR
rootcause config sk-ant-...
```

---

## Repo Details

- GitHub: https://github.com/UA9-TA/rootcause
- Local path: /Users/chitra/Documents/Projects/rootcause
- Push target: main branch
- License: MIT
