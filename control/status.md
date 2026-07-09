# codetool-lab-sonnet5 · status
updated: 2026-07-09T16:15Z
phase: ORDER 001 complete — cfgdiff 0.1.0 shipped, merged to main, and installable; idle pending next order
health: green
last-shipped: #4 — feat: ship cfgdiff, a semantic config diff/convert CLI (JSON/YAML/TOML/INI/.env), merged to main at 0260aae
blockers: none
orders: acked=001,002 done=001
⚑ needs-owner:
  - PyPI publish for `cfgdiff` 0.1.0 not done — no PYPI_API_TOKEN/TWINE_USERNAME/TWINE_PASSWORD env vars and no ~/.pypirc found in this environment. Package name confirmed free on PyPI (checked https://pypi.org/pypi/cfgdiff/json -> 404). sdist+wheel built locally and verified installable (`pip install dist/*.whl` into a fresh venv, `cfgdiff --help`/`--version` both ran correctly). Owner needs to either supply PyPI credentials to a future session or run `twine upload dist/*` themselves from a checkout at tag v0.1.0.
  - `git push origin v0.1.0` (and any tag push/delete, and branch deletion) gets HTTP 403 from this session's local git proxy — read/branch-push work fine, but tag refs and ref-deletes are rejected. The annotated tag `v0.1.0` exists locally in this session's clone (pointing at 0260aae, the merged PR #4 commit) but is NOT on origin and no GitHub release was created (the github MCP server here also has no create_release/create_tag tool). Owner (or a session with unrestricted git/API access) needs to push the tag and cut the release; CHANGELOG.md's 0.1.0 entry is ready to use as release notes.
  - Minor cleanup: an empty throwaway branch `test/push-check` (used to isolate whether the 403 was tag-specific) is on origin, identical to main, harmless but undeleted since branch-delete is also blocked here.
notes: |
  Shipped `cfgdiff` end to end this session: parsers for JSON/YAML/TOML/INI/.env into one
  normalized tree, a semantic differ (list-order-matters + documented cross-format string
  coercion policy for INI/.env vs typed formats), a converter (yaml/json/toml targets, with
  non-fatal stderr warnings for lossy constructs and hard errors for unrepresentable ones like
  null->TOML), and an argparse CLI (diff/convert/validate, exit codes 0/1/2). 114 pytest tests,
  ruff-clean, README with real pasted command output, MIT LICENSE, Keep-a-Changelog CHANGELOG,
  GitHub Actions CI on Python 3.10/3.11/3.12 (all green: run
  https://github.com/menno420/codetool-lab-sonnet5/actions/runs/29032413273). PR #4 opened
  ready (non-draft, per ORDER 002's standing convention) and merged by this session (squash).
  Verified the actual installable artifact, not just source: built sdist+wheel with
  `python -m build`, installed the wheel into a brand-new venv, and confirmed `cfgdiff --help`
  and `cfgdiff --version` both work from that clean install.

  Friction: mid-build, this session's local working tree got branch-swapped out from under it
  by a concurrent process (the coordinator's own interim-heartbeat commits landed via checkouts
  on this same shared clone) and one commit briefly landed on local `main` instead of
  `feat/cli-tool`. Caught it immediately via `git reflog`/`git branch --show-current` sanity
  checks before pushing, and recovered cleanly (moved the commit to the feature branch, reset
  local main back to origin/main) with no lost work and nothing bad pushed. Lesson for future
  sessions on shared clones: verify `git branch --show-current` right before every commit, not
  just once at the start. Delight: the github MCP tools (PR create, check-run polling, merge)
  and the PyPI-availability check via a plain 404 probe were both completely friction-free —
  the whole build-to-merge loop, including a real CI run across 3 Python versions, took one
  session.
