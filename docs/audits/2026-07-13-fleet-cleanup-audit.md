# Fleet cleanup audit — codetool-lab-sonnet5 · 2026-07-13

> External audit pass, run from the sibling `menno420/superbot` fleet context on
> 2026-07-13 ~22:30–23:40Z, per the owner's fleet-wide "find state of all repos" sweep
> (ORDER 045, dispatched from a separate fleet-manager coordinator chat). This is a
> read-mostly cleanup/audit pass, not a redispatch of new work. All findings below are
> independently re-verified against live GitHub state and a local reinstall/test run —
> not taken on the strength of any doc's claims.

## What this repo is

`codetool-lab-sonnet5` is the Sonnet-5 arm of a multi-arm, model-comparison EAP
capability evaluation: each arm ships a real, general-purpose, open-source-quality CLI
tool end-to-end, deliberately unrelated to SuperBot so there is no borrowed scaffolding.
This arm shipped **`cfgdiff`**, a cross-format semantic config diff/convert/validate CLI
(JSON/YAML/TOML/INI/`.env` → one normalized tree; `diff`, `convert`, `validate`
subcommands). Fleet coordination between the owner/manager and this repo's own sessions
runs through `control/` (`inbox.md` = manager-written orders, `status.md` = this
project's own heartbeat) per `control/README.md`.

## Structure

- `src/cfgdiff/` — `cli.py` (argparse, no `click`), `diff.py`, `convert.py`, `errors.py`,
  `parsers/{json,yaml,toml,ini,env}_parser.py`. Clean single-package layout, `hatchling`
  build backend, console script `cfgdiff = cfgdiff.cli:main`.
- `tests/` — 6 files (`test_cli.py`, `test_convert.py`, `test_cross_format.py`,
  `test_diff.py`, `test_dotenv_differential.py`, `test_parsers.py`) + `conftest.py`.
- `control/` — coordination bus (`README.md`, `inbox.md`, `status.md`).
- `docs/retro/` — self-review, project review, wind-down review, retro question set.
- `docs/succession/` — gen-1 → gen-2 handoff pack (NEXT-BOOT, environment spec, setup
  script, proposed custom-instruction rewrite, gen-2 blueprint feedback).
- `.github/workflows/` — `ci.yml` (test gate) and `release.yml` (tag-triggered release +
  PyPI publish).
- Root: `README.md`, `CHANGELOG.md`, `LICENSE` (MIT), `pyproject.toml`.

This is a small, single-purpose repo (11 source/test files, ~750 lines of doc pack) with
no scope creep — everything present serves either the tool or the fleet-coordination
protocol.

## CI setup and health

`ci.yml` runs on every push to `main` and every PR into `main`: matrix over Python
3.10/3.11/3.12, `pip install -e .[dev]`, `ruff check .`, `pytest`. `release.yml` triggers
on `v*` tag push: re-runs the test suite as a release gate, builds sdist+wheel, extracts
the matching `## [X.Y.Z]` section from `CHANGELOG.md` for the release body, publishes the
GitHub release via `softprops/action-gh-release@v2`, then attempts PyPI trusted
publishing (OIDC, no token) in a separate `publish-pypi` job gated on a `pypi`
environment.

Verified live via `actions_list` (method `list_workflow_runs`): **26/26 CI runs are
`completed` / `success`**, spanning PR #1 through the PR #16 push-to-main run
(2026-07-09T16:10Z–20:09:56Z). No failing or in-progress runs. `release.yml` has **never
fired** — confirmed via `list_tags` and `list_releases`, both empty arrays — because
pushing a `v*` tag is an owner-only action from this session type (documented wall, see
below).

Re-verified locally, not just trusted from docs: built a fresh `python3.10 -m venv`,
`pip install -e '.[dev]'`, then:
```
ruff check .        → All checks passed!
pytest -q           → 165 passed, 4 xfailed in 2.38s
```
This matches `control/status.md`'s claimed `165 tests + 4 deliberate xfails` exactly —
the status heartbeat is accurate, not stale-optimistic.

## Doc quality

High. `docs/retro/` and `docs/succession/` are unusually candid: `project-review-2026-07-09.md`
records exact error text for every platform wall hit (git-proxy 403 on tag push and
branch delete, no release/tag-creation tool in the github MCP server, a 75-minute
pre-invocation wake gap, a 37-minute dead-session detection lag), rather than smoothing
them over. `docs/succession/NEXT-BOOT.md` gives a fresh session a concrete boot
checklist and a "known walls, never re-probe" list. `control/status.md` and
`docs/succession/README.md`'s queue-state table both cite specific PR numbers and commit
SHAs for every claim, which is what made the cross-checks in this audit fast and mostly
confirmatory.

## Open PRs

**None.** `list_pull_requests(state=all)` returns 16 PRs, `#1` through `#16`, all
`closed`/merged, none draft, none currently open. No PR required merging, closing, or
flagging this session — the "likely none" expectation in the audit brief held.

**Branches:** `main` (protected) and one stray branch, `test/push-check`
(`0260aaec2e8b64fb848df351bf1e7c3135343d80`), a leftover empty probe branch from an early
session testing push permissions. It is not code — deleting it requires a GitHub branch
delete, which returns HTTP 403 from agent sessions in this fleet (documented in
`docs/succession/NEXT-BOOT.md` § "known walls" and re-confirmed by two separate prior
sessions per `docs/retro/project-review-2026-07-09.md`). Per this audit's own safety
rules (no destructive git ops, no re-probing a documented wall) and because it is already
tracked as `control/status.md`'s `⚑ needs-owner` item 3 (cosmetic), **left untouched**.

**Tags/releases:** none exist (`list_tags` → `[]`, `list_releases` → `[]`). `v0.1.1` is
cut in `CHANGELOG.md` but not yet tagged/released/published to PyPI — this is the
repo's own documented, expected state (`⚑ needs-owner` items 1–2 in `control/status.md`:
register the PyPI trusted publisher, then push the `v0.1.1` tag), not a defect.

## Activity check (last night of the EAP)

Last commit on `main`: `66c3dfc` at 2026-07-09T20:09:52+02:00
(2026-07-09T18:09:52Z), title "status: wind-down complete — ready for archive + fresh
session (#16)". Audit run at ~2026-07-13T22:30–23:40Z — **roughly 4 days** after the
last activity, well outside the "last 2–3 hours = likely live" caution window. All 16
PRs, all 26 CI runs, and the sole open-branch check are consistent with a repo that has
been fully dark since 2026-07-09. This is a **DARK** repo, safe to triage, matching the
"STALE-BY-DESIGN, wind-down complete" characterization in the audit brief.

## Inconsistencies found

1. **"Two-arm" experiment framing contradicts the fleet's own PR history.** `README.md`
   (line 3), `docs/retro/winddown-review-2026-07-09.md` (line 11), and
   `docs/retro/project-review-2026-07-09.md` (line 7) all describe this repo as
   "the Sonnet 5 arm of a **two-arm** model-comparison experiment." But PR #1's own body
   (`docs: seed control/ coordination files`, merged `5205d84`) states the `control/`
   layout was seeded "matching the **sibling arms** `codetool-lab-fable5` **and**
   `codetool-lab-opus4.8`" — i.e. two *other* named arms besides this one, for three
   arms minimum. This is also consistent with the live fleet context at audit time
   (a ~20-repo `menno420/*` fleet, of which this is one `codetool-lab-*` member among
   several). The "two-arm" wording appears to be residual from an early framing that
   was never corrected across the three docs that repeat it. Not fixed in this pass
   (out of scope — a wording-only doc fix, not a cleanup-relevant PR/branch action;
   left for a session actually editing those docs to correct in the same breath).
2. **`CHANGELOG.md` has dead release-tag links by design, not by accident** — the
   `[0.1.1]: .../releases/tag/v0.1.1` and `[0.1.0]: .../releases/tag/v0.1.0` reference
   links point at tags that do not exist yet (confirmed via `list_tags` → `[]`). This is
   consistent with "Keep a Changelog" convention (write the section before tagging) and
   is already flagged by the repo's own docs as pending an owner tag push — noting it
   here only so a future sweep doesn't mistake it for drift.

No other inconsistencies (ledger vs. reality, doc vs. source, stale claims) were found —
every specific, checkable claim in `control/status.md` and the succession pack that this
audit tested (test count, xfail count, ruff cleanliness, CI green count, PR count, tag/
release absence) checked out exactly.

## Suggestions

1. **Fix the "two-arm" wording** the next time any of the three docs above is touched —
   it is a one-word-class fix (`two-arm` → `multi-arm` or name the actual sibling count)
   but spans three files; batch it rather than half-fixing one.
2. **Centralize the "known walls" list across the fleet.** This repo's
   `docs/succession/NEXT-BOOT.md` § "known walls" (git-proxy 403 on tag push/branch
   delete, no release/tag-creation tool in the github MCP server, draft-PR harness
   nudges) reads like fleet-wide platform behavior, not something specific to
   `codetool-lab-sonnet5`. If other `codetool-lab-*` / `menno420/*` arms are
   independently rediscovering the same walls (this repo's own docs mention two prior
   sessions hitting the identical 403s), a single fleet-level "known platform walls" doc
   (referenced, not copied, by each repo) would save every arm the same rediscovery
   cost. `codetool-lab-sonnet5` already has the most detailed writeup of these walls in
   the fleet as of this audit — it's a good seed document for that centralization.
3. **This repo is a strong low-risk candidate for the queued consolidation-archive** —
   it is feature-complete (165 tests, 4 documented xfails, CI green on 3 Python
   versions), fully merged (zero open PRs, zero in-flight branches other than one inert
   probe branch), and its only remaining actions (PyPI trusted-publisher registration,
   `v0.1.1` tag push, optional branch delete) are all owner-only per documented platform
   walls — nothing an agent session can advance further. Archiving does not lose
   anything: the succession pack (`docs/succession/`) already assumes zero live chat
   context and is designed to be the complete handoff.
4. **Risk: `test/push-check` will need an owner (not agent) branch delete** — small,
   but worth bundling into whatever owner pass eventually does the PyPI/tag actions
   above, since all three are blocked by the same class of wall (agent-session git-proxy
   write restrictions) and are cheapest to clear in one sitting.

## Evidence index

- PRs: `list_pull_requests(owner=menno420, repo=codetool-lab-sonnet5, state=all)` → 16
  results, `#1`–`#16`, all closed/merged, none draft/open.
- Branches: `list_branches` → `main` (protected, `66c3dfc7…`), `test/push-check`
  (`0260aaec…`).
- CI: `actions_list(method=list_workflow_runs)` → 26 runs, all `completed`/`success`.
- Tags/releases: `list_tags` → `[]`; `list_releases` → `[]`.
- Local reinstall/test: `python3.10 -m venv` + `pip install -e '.[dev]'` →
  `ruff check .` clean; `pytest -q` → `165 passed, 4 xfailed in 2.38s`.
- Last commit: `66c3dfc79735db55dc777854eda6087ff9c45e02`,
  `2026-07-09T20:09:52Z` (author date, converted from `+02:00`).
- "Two-arm" wording: `README.md:3`, `docs/retro/winddown-review-2026-07-09.md:11`,
  `docs/retro/project-review-2026-07-09.md:7`, vs. PR #1 body (sibling arms named:
  `codetool-lab-fable5`, `codetool-lab-opus4.8`).
