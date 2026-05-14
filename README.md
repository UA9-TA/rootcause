# RootCause 🔍

> Point it at any failing test. Get the exact fix.

![RootCause](https://img.shields.io/badge/AI-Powered%20Debugging-blue?style=for-the-badge)

RootCause is an open-source CLI tool that performs AI-powered root cause analysis on failing tests and runtime errors. Instead of "asking ChatGPT about your code," RootCause systematically captures the full execution trace, gathers context, and returns the exact root cause + fix in plain English.

<!-- Add demo.gif here -->

## Installation

```bash
pip install rootcause
```

## Quick Start

```bash
# Analyze a failing pytest test
rootcause pytest tests/test_auth.py::test_login

# Analyze a failing jest test
rootcause jest src/__tests__/auth.test.js

# Analyze a raw error log
rootcause analyze error.log
```

## How it Works

```
1. Run Test ──> 2. Capture Trace ──> 3. Gather Context ──> 4. AI Analysis
(pytest/jest)   (sys.settrace/stderr) (source files + git) (Claude Sonnet)
```

## Supported Frameworks

| Framework | Status |
|-----------|--------|
| `pytest` | ✅ |
| `jest` | ✅ |
| `mocha` | ✅ |
| `rspec` | 🔜 |
| `go test` | 🔜 |

## Configuration

Set your Anthropic API key to use the tool:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# OR
rootcause config sk-ant-...
```

## Why not just ask ChatGPT?

ChatGPT requires you to manually copy-paste the error log, track down the failing source code, and copy that in too. You might miss important files, or not paste the exact lines that caused the failure.

RootCause uses a systematic approach:
1. Runs the test and collects execution traces.
2. Extracts exactly the source code involved.
3. Automatically fetches recent Git changes to give the AI complete context.
4. Uses an advanced Claude prompt to return structured fixes.

## Contributing

We welcome contributions! Please see our guidelines for more details. To get started:

```bash
git clone https://github.com/UA9-TA/rootcause.git
cd rootcause
pip install -e ".[dev]"
pytest tests/
```

## License

MIT License
