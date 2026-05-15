# Changelog

All notable changes to RootCause are documented here.

## [0.1.0] — 2026-05-15

### Added
- `rootcause pytest <test>` — analyze failing pytest tests with AI
- `rootcause jest <test>` — analyze failing Jest tests
- `rootcause mocha <test>` — analyze failing Mocha tests
- `rootcause analyze <file>` — analyze raw error logs and tracebacks
- `rootcause last` — analyze the last error from shell history
- `rootcause config <key>` — save Anthropic API key to `~/.rootcause/config.toml`
- `--auto-fix` flag — apply the suggested fix without confirmation prompt
- Execution tracing via `sys.settrace` for richer AI context
- Git history context (last 5 commits touching failing files)
- Source code context (±30 lines around each failure location)
- Rich terminal output with colored confidence scores and syntax-highlighted diffs
- Unified diff auto-patch with confirmation dialog
