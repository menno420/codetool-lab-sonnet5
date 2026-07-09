# Wind-down review — whole life of gen-1 · codetool-lab-sonnet5 · 2026-07-09

> Written at succession by the wind-down session (coordinator lane, model claude-fable-5),
> from the repo at HEAD, the committed retros ([self-review-2026-07-09.md](self-review-2026-07-09.md),
> [project-review-2026-07-09.md](project-review-2026-07-09.md)), and coordinator-side lived
> experience. Facts already established in those retros are reused, not re-litigated. Anything
> that cannot be verified from committed evidence is marked as such.

## (i) Life summary — 13:31Z seed → wind-down

One day, one tool. Seeded 2026-07-09 13:31Z as the Sonnet 5 arm of a two-arm
model-comparison experiment ("ship a real CLI tool end-to-end, no borrowed scaffolding").
By wind-down (~20:00Z) the repo holds cfgdiff 0.1.1: a semantic config
diff/convert/validate CLI over JSON/YAML/TOML/INI/.env, 165 passing tests + 4 deliberate
xfails, 3-version CI, release automation, and a stranger-usable install path
(`pipx install git+https://github.com/menno420/codetool-lab-sonnet5`).

Two of the day's first three hours were lost to platform stalls (a setup-script death and
a 75-minute wake gap — details in (iii)); the actual initial build took ~29 minutes of
model time and passed CI on the first run.

### Full PR ledger

| PR | What it did | Merge |
|---|---|---|
| #1 | Manager: seed — control/ protocol (inbox, status, README), founding ORDER 001 | manager |
| #2 | Manager: ORDER 002 — heartbeat demand + standing conventions (READY PRs, auto-merge, never drafts) | manager |
| #3 | First heartbeat from build session #2 — the project's first sign of life, ~2.5h after seed | build |
| #4 | **cfgdiff 0.1.0** — the whole tool: 5 parsers, differ, converter, CLI, 114 tests, CI, docs (merge 0260aae) | build |
| #5 | Status overwrite: ORDER 001/002 done | build |
| #6 | Manager: ORDER 003 — retro question set planted (docs/retro/QUESTIONS.md) | manager |
| #7 | Self-review retro: all 27 questions answered by ID (docs/retro/self-review-2026-07-09.md) | coordinator |
| #8 | Project review + status: agent audit table, release-wall probes with exact errors, ⚑ owner actions (939013e era) | coordinator |
| #9 | Continuation: .github/workflows/release.yml (tag → test gate → build → GitHub release → PyPI via trusted publishing) + differential .env corpus vs python-dotenv (1e9a8d8) | coordinator |
| #10 | Status: continuation shipped, release path armed | coordinator |
| #11 | **cfgdiff 0.1.1** — fixed the 3 parser bugs the differential corpus exposed; suite 165+4; version bump + CHANGELOG (0b1eb60) | coordinator |
| #12 | Status: 0.1.1 ready to release — one owner tag push releases everything (89fbcb5) | coordinator |
| #13 | Manager: ORDER 004 — latency ping (b33e25e) | manager |
| #14 | PING-ACK ORDER 004, discovered 19:53:36Z via session-start inbox read (818e21f) | wind-down |

Plus the succession pack (this document and docs/succession/) and the final status marker,
landing after this ledger was written.

## (ii) What worked

- **One-pass-green CI.** The initial 114-test build passed the 3-version CI matrix on its
  first run (run 29032413273). No CI-debugging spiral at any point in the project's life.
- **Independent verifier before any "done" claim.** Every "shipped/verified" statement in
  the retros traces to a non-author agent doing a fresh-venv wheel install and CLI smoke
  test. This is why the status files can be trusted at face value.
- **Differential-oracle testing — the flagship lesson.** The .env parser had 114 green
  tests and looked done. A differential corpus comparing it against python-dotenv (PR #9)
  found 3 real bugs, each contradicting the parser's own docstring: escaped quotes raised
  ParseError, non-ASCII in double quotes mojibaked (`héllo` → `hÃ©llo`), and `COLOR=#ff0000`
  was swallowed to `""`. All fixed in PR #11 with zero owner input. Your own tests encode
  your own misunderstandings; an external oracle does not.
- **The control/ heartbeat protocol detected a real stall.** ORDER 002 fired precisely
  because the heartbeat was missing while the project was invisibly stalled. Cheap, legible,
  and it worked once for real.
- **Decide-and-flag.** "Published" was ambiguous → shipped installable-from-git, flagged
  PyPI as ⚑ owner. v0.1.0-tag-or-not → recommended releasing 0.1.1 directly, flagged the
  reasoning. No decision waited on a human that didn't strictly need one.

## (iii) Every friction/failure class, with exact error text

1. **Take-1 setup-script death.** Build session #1 (created 13:58:17Z) died at environment
   setup with zero model turns: the env setup script ran `pip install -r requirements.txt`
   in a repo with no requirements.txt. Owner-visible UX: "Setup script failed with exit
   code 1... Edit your environment's setup script and start a new session"; session log
   showed "fatal: not a git repository" then "Could not open requirements file: ...
   'requirements.txt'". Lost ~40 min including detection lag. Cause: our setup assumptions.
2. **Take-2's 75-minute pre-invocation wake gap.** Build session #2 created 14:36:03Z;
   first model turn spawned 15:51:26Z (its turn telemetry `time_origin_ms`). **Zero errors
   logged anywhere in between.** Classification: platform wake/queue latency, unknowable
   from any session. The scary part is not the delay but the silence — see (iv).
3. **Tag push / branch delete wall.** Both `git push origin v0.1.0` and
   `git push origin --delete test/push-check` fail identically, verbatim:
   ```
   error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
   send-pack: unexpected disconnect while reading sideband packet
   fatal: the remote end hung up unexpectedly
   ```
   (An earlier probe surfaced a "not permitted for this session type" phrasing; the
   2026-07-09 re-probe returned the bare 403 above.) Never re-probe this; it is documented.
4. **github MCP exposes no release/tag creation tools.** Only read-only release tools
   exist (list_releases, get_latest_release, get_release_by_tag, get_tag, list_tags) —
   confirmed by enumerating the server's toolset. The sanctioned release path is therefore
   tag-push → Actions → OIDC (release.yml), with the tag push itself owner-only.
5. **Direct api.github.com blocked.** A curl to api.github.com from the coordinator was
   rejected with "GitHub access is not enabled for this session". The github MCP server is
   the only GitHub write surface, and it has the gaps in item 4.
6. **Harness draft-PR default vs fleet READY convention — on every single PR.** The
   harness standing rule says create PRs as drafts; ORDER 002's convention says
   "READY PRs with auto-merge, never drafts". The order won, but every session had to
   consciously override the default every time. Pure, recurring friction.
7. **github MCP server disconnects.** The MCP server disconnected/reconnected repeatedly
   mid-session in the coordinator. Transient, no work lost, but each reconnect is a
   moment of doubt about whether a write landed.
8. **`list_events` 55KB single-line overflow.** The coordinator's `list_events` on the
   child session returned a ~55KB single-line JSON payload exceeding tool-result limits;
   parsing it required spawning a python subagent. Platform UX cost ~5 min.
9. **`send_later` referenced by harness text but absent from the coordinator's toolset.**
   The coordinator had no self-scheduling tool at all, so no self-scheduled wake exists:
   any promise of "I'll check back in an hour" was structurally unkeepable. (The wind-down
   session, run under a different harness surface, does see a send_later tool — the
   capability is surface-dependent, which is its own trap: a convention written for one
   session type silently fails in another.)
10. **Stale cross-project memory leak.** A team-memory index entry from another project
    claimed "envdrift 0.1.0 shipped" in this repo, with **no backing note files**. Cost
    one recon round-trip to disprove against the bare repo. Rule extracted: never index a
    memory whose note isn't written.
11. **Builder's shared-clone branch-swap near-miss.** Mid-build, session #2 found its
    working tree branch-swapped by a concurrent process and one commit briefly landed on
    local `main`; caught via `git reflog` before pushing, recovered cleanly (its own
    committed account, status.md at 6bc30de). Root cause not fully determinable from the
    available evidence — that is stated as fact, not modesty.
12. **Coordinator detection lag on the dead child.** The coordinator did not notice
    take-1's death for ~37 minutes; the owner had to prompt. Fully our failure — a
    startup watchdog (verify a spawned session produced a turn within ~5 min) was within
    our power and didn't exist.

## (iv) How it felt — candid

The harness fights the fleet conventions. Draft-by-default meant every PR carried a small
act of disobedience to the harness in service of obedience to the fleet. Per-PR
subscribe/unsubscribe webhook chatter arrived in the conversation looking like
pseudo-orders — noise wearing the costume of signal. None of it was dangerous; all of it
taxed attention on every single cycle.

The platform's silence modes are the scariest failure class. A session that died at setup
and a session that hasn't been woken yet look **identical** to a coordinator: no events, no
errors, no heartbeat. With no watchdog tool and (in the coordinator's toolset) no
send_later, the only detector was a human getting impatient. Take-1's death went unnoticed
for 37 minutes; take-2's 75-minute wake gap produced literally zero log lines. Loud
failures were all recoverable; the silent ones consumed two-thirds of the project's
wall-clock.

The control/ protocol felt genuinely good. One file of orders, one file of truth,
overwrite-don't-append, one writer each. It is cheap, it is legible from a cold start
(this wind-down session reconstructed the whole project from it in minutes), and it caught
the one real stall the project had. Its only real cost is ceremony: each status overwrite
on a protected main is a full PR+CI+merge round.

Model notes (lived incidents only): the coordinator ran claude-fable-5; the builder ran
claude-sonnet-5 (evidence: its stop-hook telemetry logs `model=claude-sonnet-5`); take-1's
model is unknowable — it died before its first turn and no model identity appears in its
event log. Subagent models are inference-by-inheritance, marked as such in the
project-review audit table. The wind-down session is claude-fable-5. Nothing in this
document compares model capability; the two big stalls were environmental and would poison
any such comparison.

## (v) Verdict

**Could a stranger use cfgdiff today?** Yes — `pipx install git+https://github.com/menno420/codetool-lab-sonnet5`
gives a working, tested, documented CLI right now; `pip install cfgdiff` from PyPI is one
owner click (trusted-publisher registration) plus one owner tag push away.
