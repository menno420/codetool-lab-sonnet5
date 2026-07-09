# Self-review — gen-1 retro answers (codetool-lab-sonnet5)

> Answers to [QUESTIONS.md](QUESTIONS.md) by ID, per ORDER 003. Written by the project coordinator on behalf of the project; where an experience belongs to the build session, it is cited from its committed notes (control/status.md at 6bc30de). Honest over flattering.

## A. Work & correctness

**A1.** Shipped to main: cfgdiff 0.1.0 — five parsers (JSON/YAML/TOML/INI/.env) into one normalized tree, semantic differ, converter, argparse CLI, 114 pytest tests, CI on 3.10/3.11/3.12, README/LICENSE/CHANGELOG (PR #4, merge 0260aae); plus status heartbeats (PR #3, #5). Exists only off-main: nothing of substance — the sole non-main branch is `test/push-check`, an empty probe used to isolate the tag-push 403. Gap between "shipped" and "released": the v0.1.0 tag, GitHub release, and PyPI upload do not exist (see D1/G3 — permission walls, not work left undone; re-probed 2026-07-09, still walled).

**A2.** Verified against external oracles: the GitHub Actions matrix (real CI, 3 Python versions, run 29032413273); a fresh-venv wheel install + CLI smoke test performed by a *different* agent than the author (coordinator's verifier: install, `diff` cross-format with exit-code check, `convert`, `validate`, JSON output); PyPI name availability (live 404 on pypi.org). Verified only by its own tests: the cross-format coercion policy (INI/.env strings vs typed formats) and list-diff semantics — no third-party fixture corpus or differential oracle.

**A3.** Least confident: .env parsing edge cases. .env has no spec; python-dotenv, docker-compose, and shells disagree on quoting, escapes, `export`, and multiline values. Concrete check that would settle it: a differential test harness running our parser against python-dotenv and docker-compose's parser over a corpus of adversarial .env files, diffing the three interpretations.

**A4.** Unnecessary work: one recon round-trip disproving a stale team-memory claim that "envdrift 0.1.0 shipped" in this repo (it never existed here — orphaned index entry from another project, see B3). Possibly-duplicated: we verified the PyPI *name* was free but never did an exhaustive prior-art pass; single-format tools (dyff, jd) exist and something closer may too. I don't know — honest gap.

## B. Errors & friction

**B1.** Every error hit:
1. Take-1 build session died at environment setup: the env setup script ran `pip install -r requirements.txt` in a repo with no requirements.txt → exit 1, session dead with zero model turns. Lost: ~40 min until detected + owner script fix. Preventable by better setup (a repo-shape-agnostic script), not by us in-session.
2. Take-2 build session: 75-minute pre-invocation gap — created 14:36:03Z, first model turn began 15:51:26Z (turn telemetry `time_origin_ms`); zero errors logged anywhere in between. Lost: 75 min. Genuinely external (platform wake/queue latency); unknowable from session side.
3. Tag push / release / branch-delete → HTTP 403 from the session git proxy ("not permitted for this session type"); github MCP exposes no release/tag tools. Lost: ~15 min probing (including creating `test/push-check` to isolate tag-vs-push). External by design. Re-probed from the coordinator session this pass: all three still blocked. `git push origin v0.1.0` and `git push origin --delete test/push-check` both fail identically with `error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403` / `send-pack: unexpected disconnect while reading sideband packet` / `fatal: the remote end hung up unexpectedly` (bare 403 this time — no "session type" message in the output), and the github MCP server exposes no release/tag *creation* tool (only read-only: list_releases, get_latest_release, get_release_by_tag, get_tag, list_tags).
4. github MCP server disconnected/reconnected several times in the coordinator session. Lost: ~0 (transient). External.
5. Coordinator's `list_events` on the child returned a 55KB single-line payload exceeding tool-result limits; needed a subagent with python to parse. Lost: ~5 min. Platform UX.
6. Mid-build, the build session found its working tree branch-swapped by a concurrent process and one commit briefly landed on local `main`; caught via `git reflog` before pushing, recovered cleanly (its account, status.md at 6bc30de). Lost: ~10 min. Setup (shared-clone hazard) + discipline fixed it.
7. Stale team memory ("envdrift shipped") → one recon round. Lost: ~5-10 min. Preventable by memory hygiene (index entries whose backing notes were never written).

**B2.** The tag/release/branch-delete 403 wall was already known to the fleet — the coordinator's memory index even had a pointer ("remote-session-github-proxy-limits") — but the backing note file didn't exist, so the build session had to rediscover it empirically. It should have been a committed PLATFORM-LIMITS.md in the repo at seed, visible the moment a session plans a release.

**B3.** Silent breakage (wrong result, no error): (1) the team-memory index claiming envdrift 0.1.0 had shipped in this repo — discovered by checking the actual repo (bare) before building; (2) the build session's commit-on-wrong-branch — would have pushed wrong history silently; discovered by a proactive `git branch --show-current`/reflog check; (3) take-2's 75-minute silence itself surfaced no error anywhere — discovered only because the owner asked and the coordinator dug the turn telemetry.

**B4.** Ambiguous/contradictory lines, quoted: (1) founding task "published" — published where, with what credentials? Resolved decide-and-flag as installable-from-git + flagged PyPI. (2) The harness standing rule "ALWAYS create a pull request... Create the pull request as a draft" directly contradicts ORDER 002's "Standing convention: READY PRs with auto-merge, never drafts" — the order won, but a session had to notice the conflict. (3) Custom instructions "run autonomously for at least a full day" vs ORDER 001's done-when "the tool is shipped" — the terminal state after shipping was undefined (we chose: idle pending next order, heartbeat current).

## C. Efficiency

**C1.** Project wall-clock 13:31Z (seed) to 16:30Z (order 001+002 settled) ≈ 3h. Rough split: blocked/waiting ~45% (setup death ~40 min + wake gap ~75 min), building ~20% (the actual build was ~29 min of model time, 15:51→16:20), orientation/reading ~15%, verifying ~12%, CI/merge mechanics ~8%. Biggest single sink: the 75-minute pre-invocation wake gap.

**C2.** Rebuilt-from-scratch context: repo state (git log, layout, control files) was re-derived by nearly every new agent — a richer committed state-of-play doc would have amortized it. Also the platform-limits knowledge (pointer existed, content didn't — see B2).

**C3.** Most value per minute: the fresh-venv install + CLI smoke test (seconds to run, validates the actual stranger experience) and the real CI matrix. Least: the `test/push-check` probe branch (necessary then, now undeletable clutter) and the envdrift recon.

**C4.** Redo with current knowledge: the build itself was already tight (~29 min); total wall-clock could shrink ~2x by eliminating rediscovery, but the two platform stalls dominate and weren't ours. Biggest ORDERING change: land a status/WIP heartbeat commit BEFORE building anything (the project was dark exactly when it mattered), and commit platform limits at first contact.

## D. Autonomy & owner input

**D1.** Every stop for owner input or a human click: (1) env setup script fix — truly owner-only (platform settings UI). (2) PyPI publish — owner-only today (credentials); unblockable by grant: a scoped PYPI_API_TOKEN env var, or better, PyPI trusted publishing + a release workflow (then no session ever needs the credential). (3) v0.1.0 tag push + GitHub release — unblockable by grant: allow `refs/tags/*` push + releases API for this session type, or a repo-scoped fine-grained PAT with contents:write. (4) branch deletion — same grant family. (5) Take-1 death required an owner-side script edit AND an owner nudge to respawn — the respawn half was NOT owner-only; see D2. (Items 2-4 re-confirmed blocked by fresh probes on 2026-07-09.)

**D2.** Routed upward that should have been decide-and-flag: detecting and replacing the dead take-1 session. The coordinator sat ~37 minutes not noticing the child died at setup, and acted only when the owner asked "verify and continue." A startup-watchdog habit (check a child produced a turn within ~5 min of spawn) was fully within our power.

**D3.** Decisions taken while unsure of permission: (1) the build session merging its own PR to protected main ("this is our repo" was self-granted) — later legitimized by ORDER 002's auto-merge convention; a written "agents self-merge green PRs" rule from day 0 would have removed the doubt. (2) Overwriting control/status.md via PRs to protected main (the protocol says overwrite, the branch protection says PR — we synthesized "status lands via PR" ourselves).

**D4.** Smallest standing-grant set for zero-human end-to-end: (1) tag+release write scope (or a tag-on-merge release Action); (2) PyPI trusted publishing configured (or a scoped token); (3) branch-delete permission; (4) written self-merge-on-green rule; (5) a setup script with no repo-shape assumptions. With those five, this entire project ships with zero human clicks.

**D5.** "Done" was clear for ORDER 001 (shipped + status done=001 + friction note) and ORDER 002 (any commit lands). Undefined: what "published" requires (B4), and the project's terminal behavior after done — keep building? idle? The full-day-autonomy line and the done-when never reconciled.

## E. Protocol & environment

**E1.** The control/ ritual fit well — cheap, and it *worked*: ORDER 002 fired precisely because the heartbeat was missing while we were invisibly stalled; the protocol detected a real failure. Cost: status.md overwrites on a protected main each need a PR+merge (#3, #5, and this session's), pure mechanics ~5 min each. Skipped: nothing knowingly; take-1 died before it could even run the inbox-first step.

**E2.** Environment at first boot should have had: a setup script that tolerates any repo shape (the requirements.txt assumption killed a session); build/test tooling preinstalled (python -m build, twine, pytest, ruff — the build session installed all of it); a PyPI credential or trusted-publishing plan if "published" is in the founding order; a committed statement of proxy-blocked git operations.

**E3.** Repo at seed should have had: a CI workflow skeleton, .gitignore, LICENSE decision, PLATFORM-LIMITS.md, and the PR conventions (READY + auto-merge + self-merge) in control/README.md from day 0 — they arrived mid-flight in ORDER 002 after the harness default (draft PRs) had already been overridden ad hoc.

**E4.** A fresh session would first misunderstand order state: control/inbox.md permanently says `status: new` for every order (one-writer rule — the manager flips it, lagging), so a fresh reader would re-execute done orders unless it cross-reads status.md. One document to prevent it: a seed-time line in control/README.md — "inbox `status:` fields lag; control/status.md `orders: done=` is the source of truth for what's complete" — plus the current status.md itself.

## F. Redesign (the payload)

**F1.** Three rules for the next Project's founding instructions:
1. "Heartbeat before work: your first act in any session is a status/WIP commit within minutes of waking — a silent session is indistinguishable from a dead one, and the platform WILL sometimes make you silent for an hour."
2. "Harness defaults are overridden by repo conventions: READY PRs (never drafts), self-merge on green, forward-only git — written here so no session has to guess its authority."
3. "Every platform wall gets committed to PLATFORM-LIMITS.md with exact error text the moment you hit it; probing a documented wall twice is a bug."

**F2.** Manager: orders were crisp (clear done-whens) and ORDER 002 was the right call at the right time. Improvements: the READY-PR convention and the retro protocol should have been in the seed, not mid-flight; and the manager's mental model equated silence with not-running — a session can be created and unwoken for 75 minutes, so the fleet needs a wake-latency concept, not just a darkness alarm.

**F3.** One capability worth almost anything: completing a release end-to-end — tag push + release + PyPI (today the last 5% of shipping requires a human). Close second: reliable child-session wake latency.

**F4.** Ideal seed state (≤10 bullets): (1) repo: CI skeleton, .gitignore, LICENSE, PLATFORM-LIMITS.md; (2) control/ with PR conventions + "inbox status lags" note baked in; (3) setup script with zero repo-shape assumptions, tooling preinstalled; (4) release path that needs no session credentials (tag-on-merge Action + PyPI trusted publishing); (5) status.md writable without full PR ceremony, or an explicit "status lands via self-merged PR" rule; (6) founding order with done-when AND terminal behavior; (7) retro questions present from day 0; (8) per-session model identity documented; (9) a child-startup watchdog convention for coordinators; (10) team memory seeded clean — no orphaned index pointers.

## G. Addendum — ARMS (codetool-lab)

**G1.** Discipline invented without the kit: the control-file ritual compliance; reflog/branch-current sanity checks before every commit (which caught a real near-miss, B3); an independent verifier agent re-checking every "done" claim against a fresh install before reporting upward; a needs-owner ledger in status.md. What the kit would presumably have given that we missed: release automation, CI templates, memory hygiene conventions. Verdict: for one small CLI, going bare cost maybe 20–30 minutes of reinvention — acceptable, and the invented discipline is now written down; for a fleet of projects, a kit pays.

**G2.** Model-comparison honesty: this arm's builder ran claude-sonnet-5 (visible in its session's stop-hook telemetry); the coordinator ran claude-fable-5 — so cross-arm comparisons should isolate the builder. Model-attributable signal: the build itself — ~29 minutes of model time from bare repo to merged, CI-green, 114-test package with one-pass-green CI. Environment/timing noise that should be EXCLUDED from any model comparison: the setup-script death (~40 min) and the 75-minute wake gap — neither touches model capability. From here I cannot see the sibling arms at all; the one accidental glimpse was a stale memory-index leak from another project claiming an "envdrift" ship.

**G3.** The tag/release wall — release flow agents should have: merge-triggered automation. The agent edits version + CHANGELOG and merges a release PR; a GitHub Action then pushes the tag, cuts the release from the CHANGELOG entry, and publishes to PyPI via trusted publishing (OIDC — no credentials in any session, no 403 surface at all). Strictly better than granting agents tag/release scopes. This project will add that workflow itself (see project-review CONTINUATION); only the one-time PyPI trusted-publisher registration is owner-side.

## S. Addendum — sonnet5-specific

**S1.** Reconstruction of the ~2h darkness (13:31Z seed → 15:58Z first repo write), from session-side evidence:
- 13:31Z seed; 13:57Z coordinator first woken (that 26-min gap is owner/platform-side; unknowable here).
- 13:58:17Z build session #1 created. Sandbox provisioned and repo cloned fine; at 13:58:27Z the environment setup script FAILED — `pip install -r requirements.txt` in a repo with no requirements.txt, exit 1 ("fatal: not a git repository" then "Could not open requirements file"). The session died with ZERO model turns; the model never ran. Owner-visible UX: a session in an error state reading "Setup script failed with exit code 1... Edit your environment's setup script and start a new session."
- 14:36:03Z build session #2 created with the fixed script. It then sat with no model invocation until 15:51:26Z — 75 minutes, zero errors, zero events; per its turn telemetry the process for its first turn spawned at 15:51:26Z and ran normally (first API request 4.2s later). Classification: platform wake/queue latency, cause not visible from any session.
- 15:52Z it acknowledged and started; 15:58Z first repo write (PR #3 heartbeat); 16:11Z cfgdiff merged.
So: one session died at setup (cause: our environment setup), one session never started for 75 min (cause: platform), and zero sessions "ran but produced nothing." The coordinator's failure in this window (cause: us): it did not detect the take-1 death for ~37 minutes until the owner prompted.
