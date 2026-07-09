# codetool-lab-sonnet5 · status
updated: 2026-07-09T17:11Z
phase: continuation shipped: release automation ready; awaiting owner release actions
health: green
last-shipped: #9 — ci: tag-triggered release automation + .env differential test corpus, merged to main at 1e9a8d8
blockers: none
orders: acked=001,002,003 done=001,002,003
⚑ needs-owner:
  - PyPI publish of cfgdiff 0.1.0: clone the repo, `python -m build`, `twine upload dist/*` with a pypi.org API token (username `__token__`). Name confirmed free. Full click-by-click steps in docs/retro/project-review-2026-07-09.md §(e)1. (Alternatively, do item 3 first and just push the tag — the new workflow then publishes to PyPI too.)
  - Push tag v0.1.0: `git tag -a v0.1.0 0260aae -m "cfgdiff 0.1.0" && git push origin v0.1.0`. NEW since #9: the tag push now triggers .github/workflows/release.yml, which runs the test gate, builds sdist+wheel, and creates the GitHub release automatically with the CHANGELOG 0.1.0 section as body and artifacts attached — the manual "Draft a new release" step in §(e)2 is no longer needed. Tag push itself is still owner-only (agents get HTTP 403 at the git proxy, re-probed 2026-07-09).
  - PyPI trusted publishing registration (2 min, biggest payoff): pending publisher for menno420/codetool-lab-sonnet5, workflow `release.yml`, environment `pypi` — the workflow's publish-pypi job needs this; until then it fails cleanly (OIDC invalid-publisher) without affecting the GitHub release. Steps in §(e)3. Do this BEFORE pushing the tag and the whole release (GitHub release + PyPI) is one `git push origin v0.1.0`.
  - Delete leftover probe branch `test/push-check` (cosmetic): branch delete re-probed 2026-07-09, still HTTP 403 for agents. §(e)4.
notes: |
  Continuation per project-review §(f) executed with zero owner input: PR #9 (READY,
  squash-merged on green CI) added (1) .github/workflows/release.yml — on v* tag push: pytest
  gate, python -m build, GitHub release via softprops/action-gh-release@v2 with the matching
  CHANGELOG section extracted as the body and dist/* attached, then PyPI publish via trusted
  publishing (pypa/gh-action-pypi-publish, environment `pypi`, id-token: write); and (2) a
  48-case differential .env corpus (tests/test_dotenv_differential.py) checking our parser
  against python-dotenv's dotenv_values (dev-extra dependency only; runtime deps unchanged),
  closing the retro A3 confidence gap. Suite is now 155 passed + 7 strict xfails (was 114).
  Honest note: the differential corpus found 3 real gaps in our .env parser that contradict its
  own docstring — escaped \" inside double quotes raises ParseError (closing-quote scan is
  escape-unaware); non-ASCII inside double quotes gets mojibaked by the utf-8→unicode_escape
  round-trip ("héllo" → "hÃ©llo"); and a value-initial `#` in unquoted values swallows the
  value (COLOR=#ff0000 → ""). All three are kept as strict xfails with honest reasons (not
  "documented divergence") and are the top follow-up candidates for a 0.1.1. The other 4
  xfails are deliberate documented policy (shell-literal single quotes ×2, full unicode_escape
  repertoire, whitespace-preceded `#` starts a comment). The release workflow itself is
  untestable from here (tag push is owner-only), but YAML is validated, the changelog
  extraction was dry-run against the real CHANGELOG for both present and missing versions,
  and python -m build was smoke-tested locally.
