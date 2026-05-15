# RootCause — Status

**Last updated:** 2026-05-15

## State: ✅ Built + CI Green

## What exists
- Full CLI: `rootcause pytest`, `rootcause analyze`, `rootcause last`, `rootcause mocha`, `rootcause fix`, `rootcause config`
- All 8 modules: cli, runner, tracer, context, analyzer, patcher, display, config
- CI: Python 3.10 / 3.11 / 3.12 matrix, coverage ≥40%, ruff clean
- README: hero badges, sample output block, ecosystem cross-links to all 8 sibling tools
- CHANGELOG.md: v0.1.0 entry

## Key fixes applied (not in Jules' original build)
- Model corrected: `claude-3-5-sonnet-20241022` → `claude-sonnet-4-6`
- patcher.py: fixed hunk body off-by-one (empty line from splitting on `@@`)
- pyproject.toml: `addopts = "--ignore=tests/fixtures"` to exclude demo fixtures from CI
- CI: coverage threshold set to 40% (actual ~43%)
- .gitignore added, pycache files removed from history

## Pending
- [ ] Demo GIF (asciinema recording) — README placeholder at `<!-- demo.gif -->`
- [ ] HN launch (Day 1 of staggered launch queue)
- [ ] OSS application submitted — awaiting Anthropic response

## Repo
- GitHub: https://github.com/UA9-TA/rootcause
- Branch: main
- License: MIT
