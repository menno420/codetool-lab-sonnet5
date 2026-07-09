# codetool-lab-sonnet5 · status
updated: 2026-07-09T17:27Z
phase: 0.1.1 ready to release — one owner tag push releases everything
health: green
last-shipped: #11 — fix: env parser escape/unicode/hash-value bugs found by differential corpus; 0.1.1, squash-merged to main at 0b1eb60
blockers: none
orders: acked=001,002,003 done=001,002,003
⚑ needs-owner:
  1. [2 min, biggest payoff] Register the PyPI trusted publisher: pypi.org → your account →
     Publishing → "Add a pending publisher" with owner `menno420`, repository
     `codetool-lab-sonnet5`, workflow `release.yml`, environment `pypi`. Click-by-click
     steps in docs/retro/project-review-2026-07-09.md §(e)3. Without this the release
     workflow's publish-pypi job fails cleanly (OIDC invalid-publisher); the GitHub
     release itself is unaffected.
  2. Push tag v0.1.1 at current main:
     `git tag -a v0.1.1 0b1eb60 -m "cfgdiff 0.1.1" && git push origin v0.1.1`.
     This single push runs the test gate, builds sdist+wheel, cuts the GitHub release
     with the CHANGELOG 0.1.1 section as body and artifacts attached, and — if item 1 is
     done first — publishes cfgdiff 0.1.1 to PyPI. Tag push is owner-only (agents get
     HTTP 403 at the git proxy). Decide-and-flag: we recommend releasing 0.1.1 directly
     and treating v0.1.0 as optional/historical — a v0.1.0 tag at 0260aae would NOT carry
     release.yml (added later, in #9), so pushing it would not fire the workflow at all;
     tag it only if you want the historical marker, expect no automation from it.
  3. Delete leftover probe branch `test/push-check` (cosmetic; branch delete re-probed
     2026-07-09, still HTTP 403 for agents). §(e)4.
  4. Alternative if you skip item 1: manual PyPI upload — `python -m build` then
     `twine upload dist/*` with a pypi.org API token (username `__token__`), full steps
     in docs/retro/project-review-2026-07-09.md §(e)1.
notes: |
  Bugfix pass executed with zero owner input: PR #11 (READY, squash-merged on green CI at
  0b1eb60) fixed all three .env parser bugs the differential corpus had flagged as strict
  "known gap" xfails, each of which contradicted the parser's own docstring:
  (1) KEY="a\"b" no longer raises ParseError — the closing-quote scan is escape-aware;
  (2) KEY="héllo" no longer mojibakes to "hÃ©llo" — escapes are decoded per-sequence
  (\n/\t/\uXXXX/\N{NAME}/octal/hex) instead of round-tripping the whole value through
  unicode_escape, so literal non-ASCII passes through and unknown escapes (\q) are kept
  literally; (3) COLOR=#ff0000 is no longer swallowed to "" — a '#' starts an inline
  comment only when preceded by whitespace (including whitespace right after '=', so
  KEY= # note is still ""). Docstring rewritten to state exactly the implemented policy.
  The 3 gap xfails were flipped to ordinary passing cases and 7 regression cases added
  (escaped quote at end / before comment, backslash before closing quote, unknown escape
  kept, color+inline-comment, bare KEY=#, non-ASCII mixed with escapes), all verified
  against python-dotenv. The 4 deliberate documented-divergence xfails are byte-for-byte
  untouched and still strict-xfail. Suite: 165 passed + 4 xfailed (was 155 + 7), zero
  warnings even under -W error::DeprecationWarning; ruff clean.
  Version bumped 0.1.0 → 0.1.1 everywhere it appears (pyproject.toml, cfgdiff.__version__,
  README status line, the --version CLI test). CHANGELOG: previous Unreleased content plus
  the three fixes moved into "## [0.1.1] - 2026-07-09"; an empty "## [Unreleased]" heading
  kept; link reference added. release.yml's changelog-extraction script was dry-run
  against the new CHANGELOG and finds the 0.1.1 section, so a v0.1.1 tag push produces a
  correctly-bodied GitHub release. Honest caveat: the tag-triggered workflow end-to-end
  remains untestable from agent sessions (tag push is owner-only), so item 2 above is its
  first real firing.
