# Project review — codetool-lab-sonnet5 · 2026-07-09

> Full self-review + wake-up pass, per owner directive of 2026-07-09. All claims verified against the repo at main `939013e` unless marked otherwise.

## (a) What this project is, and its TRUE current state

The Sonnet 5 arm of a two-arm model-comparison experiment: ship a real, general-purpose, open-source-quality CLI tool end-to-end, deliberately unrelated to SuperBot. Coordination happens through `control/` (manager writes inbox.md; project overwrites status.md).

True state, verified against the repo (not memory):
- **cfgdiff 0.1.0 is on main and works.** PR #4 (merge `0260aae`): semantic config diff/convert/validate CLI over JSON/YAML/TOML/INI/.env. Independently re-verified after merge by a non-author agent: 114/114 tests pass in a fresh venv; CI green on Python 3.10/3.11/3.12; `pip install` into a clean venv yields a working `cfgdiff` (correct diff output, JSON mode, exit codes 0/1/2). Install today: `pipx install git+https://github.com/menno420/codetool-lab-sonnet5`.
- **Not released:** no tags, no GitHub releases, not on PyPI (name `cfgdiff` confirmed free). Blocked by session-type permissions and missing credentials — probe results with exact errors in (b) below and owner actions in (e).
- 7 commits, 6 PRs (all merged, none open), branches: `main` + leftover empty probe branch `test/push-check`.
- Orders: 001 (ship) done; 002 (heartbeat) done; 003 (retro) done by this pass — answers in [self-review-2026-07-09.md](self-review-2026-07-09.md).

## (b) Agent audit — every session/agent that worked here

| # | Agent | Model | Tasked with | Actually delivered (repo-verified) | Stalls / deaths / human input |
|---|-------|-------|-------------|-------------------------------------|-------------------------------|
| 1 | Coordinator session (this one) | claude-fable-5 (per session config; fallback claude-opus-4-8 — fallback never confirmed used) | Front door: dispatch, verify, report | Concept decision (cross-format semantic config diff), 2 build-session dispatches, dead-session diagnosis, independent post-merge verification of cfgdiff, team-memory records, this review | Did NOT detect build session #1's death for ~37 min — owner had to prompt (cause: (a) our instructions/setup — no startup watchdog). github MCP server disconnected/reconnected repeatedly (cause: (b) platform, transient, no work lost). `list_events` result overflowed tool limits, needed a python subagent to parse (cause: (b) platform UX) |
| 2 | Build session #1 "Build & ship config-diff CLI" (created 13:58:17Z) | Cannot determine — it never ran a model turn; no model identity appears in its event log. Presumably the same type as #3, but that is inference, not evidence | Full cfgdiff build | Nothing — died before turn 1 | Environment setup script failed at 13:58:27Z: `pip install -r requirements.txt` with no requirements.txt → exit 1, terminal error "Edit your environment's setup script and start a new session." Cause: (a) our setup. Owner fixed the script |
| 3 | Build session #2 "…(take 2)" (created 14:36:03Z) | claude-sonnet-5 (evidence: its stop-hook telemetry logs `model=claude-sonnet-5`) | Full cfgdiff build | PRs #3 (heartbeat), #4 (cfgdiff, 114 tests, CI, docs), #5 (status). All verified merged; CI run 29032413273 green ×3 Python versions | 75-min pre-invocation gap: created 14:36:03Z, first model turn spawned 15:51:26Z (its turn telemetry); zero errors logged in between. Cause: (b) platform wake/queue latency — unknowable in detail from session side. Mid-build shared-clone branch-swap near-miss, self-recovered via reflog (its own committed account; cause (a) setup + (c) work discipline saved it) |
| 4 | Build #2's recon subagent ("check envdrift memory / repo state") | Cannot determine directly; subagents inherit the parent session's model, so claude-sonnet-5 by inheritance — inference | Verify stale "envdrift shipped" memory claim | Disproved it: repo was bare; memory index entry was orphaned (backing note files never existed) | None; cost one round-trip. Root cause of the errand: (a) fleet memory hygiene |
| 5-9 | Coordinator's worker subagents (5: repo/inbox reader ×2, memory reader, child-timeline analyst, cfgdiff verifier) | claude-fable-5 by inheritance from the coordinator (none set an override) | Read-only data collection; one wrote team-memory files; verifier ran tests + fresh-venv install + CI/API checks | All completed; the verifier's independent confirmation is the basis for every "verified" claim above | None |
| 10 | Manager (PRs #1, #2, #6 — seed, ORDER 002, retro plant) | Cannot determine — external to this project; no telemetry visible here | Fleet orders | inbox.md orders, retro question set | Not audited; outside this project's control |
| — | This pass's executor subagent (the one committing this document) | claude-fable-5 by inheritance | Probes + docs + PRs | This document, the self-review, status update | Tag push and branch delete both hit HTTP 403 at the git proxy; github MCP exposes no release/tag creation tool (exact outputs below) |

Fate-unknowable note: session #2's 75-minute gap and session #1's would-have-been model are stated as unknowable/inference above rather than guessed.

### Release-wall probe results (re-run from this session, 2026-07-09)
- `git push origin v0.1.0`:
  ```
  error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
  send-pack: unexpected disconnect while reading sideband packet
  fatal: the remote end hung up unexpectedly
  Everything up-to-date
  ```
  (The local annotated tag `v0.1.0` → `0260aae` exists; only the push is blocked. Note the 2026-07-09 proxy returns a bare HTTP 403 — the earlier "not permitted for this session type" phrasing did not appear in this run's output.)
- GitHub release creation via MCP: github MCP server exposes no release/tag *creation* tool — only read-only tools exist (list_releases, get_latest_release, get_release_by_tag, get_tag, list_tags). Confirmed by enumerating the server's toolset this pass.
- `git push origin --delete test/push-check`:
  ```
  error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
  send-pack: unexpected disconnect while reading sideband packet
  fatal: the remote end hung up unexpectedly
  Everything up-to-date
  ```

All three walls stand; every item in (e) remains owner-only.

## (c) Retro answers

All 27 questions answered by ID in [self-review-2026-07-09.md](self-review-2026-07-09.md) (ORDER 003).

## (d) Honest efficiency verdict

Wall-clock 13:31Z seed → 16:30Z orders 001+002 settled: ~3h. Of that, ~2h was lost to two stalls that had nothing to do with the work: the setup-script death (~40 min incl. detection lag — half of which was OUR detection lag) and the 75-min platform wake gap. The build itself took ~29 minutes of model time and passed CI on the first run. Verification (independent re-test) cost ~15 min and is the reason every claim above can be trusted.

What I would redo, in order: (1) heartbeat commit before any build work — the project was dark exactly when the manager checked; (2) child-startup watchdog at the coordinator — a dead child should be detected in 5 minutes, not 37; (3) commit PLATFORM-LIMITS.md at first contact with any wall; (4) only then the build, which was fine as-is.

## (e) ⚑ OWNER ACTIONS — only you can do these

1. **Publish cfgdiff to PyPI** (unblocks: `pip install cfgdiff` for strangers; the name is free and verified).
   On any machine with Python 3.10+:
   ```
   git clone https://github.com/menno420/codetool-lab-sonnet5
   cd codetool-lab-sonnet5
   python -m pip install build twine
   python -m build
   twine upload dist/*
   ```
   When twine prompts: username `__token__`, password = a PyPI API token. To get one: pypi.org → log in (create account if needed) → Account settings → API tokens → "Add API token" → name it anything, scope "Entire account" (first upload; you can re-scope to the project after) → copy the `pypi-...` string and paste it as the password.
2. **Tag + GitHub release** (unblocks: pinned installs, release automation) — the probe in (b) confirms this session cannot do it. From the same clone:
   ```
   git tag -a v0.1.0 0260aae -m "cfgdiff 0.1.0"
   git push origin v0.1.0
   ```
   Then github.com/menno420/codetool-lab-sonnet5 → Releases → "Draft a new release" → "Choose a tag" → v0.1.0 → title `cfgdiff 0.1.0` → paste the `## [0.1.0]` section of CHANGELOG.md into the description → "Publish release".
3. **(2 minutes, biggest future payoff) Register PyPI trusted publishing** so no future release ever needs a human or a token (unblocks: fully autonomous releases via the workflow this project will add — see (f)): pypi.org → Account settings (or the cfgdiff project page after first upload) → "Publishing" → "Add a new pending publisher" → Owner `menno420`, Repository `codetool-lab-sonnet5`, Workflow name `release.yml`, Environment `pypi`.
4. **Delete the leftover probe branch** (cosmetic; agents get 403 on branch deletes — re-confirmed in (b)): github.com/menno420/codetool-lab-sonnet5 → Branches → trash icon next to `test/push-check`.

## (f) CONTINUATION — what happens next with zero owner input

Starting immediately after this document lands:
1. Add `.github/workflows/release.yml`: on push of tag `v*` — build sdist+wheel, create the GitHub release from the matching CHANGELOG section, publish to PyPI via trusted publishing (activates the moment owner action 3 is done; harmless before).
2. Add a differential .env test corpus comparing our parser's readings against python-dotenv (dev-dependency only), targeting the A3 confidence gap.
3. Keep the heartbeat: status.md stays current every session; PLATFORM-LIMITS.md knowledge is preserved in this document and team memory.
