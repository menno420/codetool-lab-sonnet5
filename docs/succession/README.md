# Succession pack — gen-1 → gen-2 · 2026-07-09

Gen-1 of this project (the Sonnet 5 arm of the codetool-lab experiment) winds down here.
Everything a fresh gen-2 session needs survives in git; the chat context that built this
repo is gone. This directory is the handoff.

## The pack

| File | What it is |
|---|---|
| [NEXT-BOOT.md](NEXT-BOOT.md) | The fresh session's first 10 minutes: read order, walking-skeleton check, known walls |
| [PROPOSED-CUSTOM-INSTRUCTIONS.md](PROPOSED-CUSTOM-INSTRUCTIONS.md) | Full rewrite of the Project Custom Instructions from lived experience, with KEEP/DROP/ADD rationale |
| [ENVIRONMENT.md](ENVIRONMENT.md) | Environment spec: env var names, setup script contract |
| [setup-universal.sh](setup-universal.sh) | Defensive setup script, tested in this container (always exits 0) |
| [GEN2-FEEDBACK.md](GEN2-FEEDBACK.md) | Concrete blueprint suggestions from this lane, for the fleet's gen-2 seed standard |
| [../retro/winddown-review-2026-07-09.md](../retro/winddown-review-2026-07-09.md) | Whole-life review: full PR ledger, what worked, every failure with exact error text, candid verdict |

## Queue state at wind-down

### DONE

- **ORDER 001** (ship the tool): cfgdiff 0.1.0 shipped end-to-end — PR #4. Five parsers
  (JSON/YAML/TOML/INI/.env), semantic differ, converter, validator CLI, 114 tests, CI on
  Python 3.10/3.11/3.12, README/LICENSE/CHANGELOG. Independently verified by a non-author
  agent (fresh-venv install + CLI smoke test).
- **ORDER 002** (heartbeat + conventions): status heartbeat protocol live; READY-PR /
  auto-merge convention adopted.
- **ORDER 003** (retro): self-review answering every question in docs/retro/QUESTIONS.md —
  PR #7; project review + status — PR #8. See docs/retro/.
- **ORDER 004** (latency ping): PING-ACK landed on main — PR #14, discovered
  2026-07-09T19:53:36Z via session-start inbox read.
- **Continuation** (zero owner input): tag-triggered release automation
  (.github/workflows/release.yml) + differential .env test corpus vs python-dotenv — PR #9.
- **Bugfix 0.1.1**: the differential corpus found 3 real parser bugs in code that already
  had 114 green tests (escape-aware quote scan, per-sequence escape decoding vs mojibake,
  value-initial `#` swallowed as comment); all fixed, suite now 165 passed + 4 deliberate
  xfails — PR #11 (0b1eb60).
- **All status heartbeats**: PRs #3, #5, #8, #10, #12.

Zero open PRs. Zero open branches except leftover `test/push-check` (an empty probe branch;
undeletable from agent sessions — branch delete is HTTP 403 at the git proxy; ⚑ owner).

### IN-FLIGHT

Nothing. All work is merged to main.

### NEXT (queue for gen-2, roughly in order)

1. **Release 0.1.1** — fires automatically on the owner's tag push
   (`git tag -a v0.1.1 0b1eb60 -m "cfgdiff 0.1.1" && git push origin v0.1.1`); release.yml
   handles test gate, sdist+wheel, GitHub release with CHANGELOG body, and PyPI publish (once
   the owner registers the trusted publisher). Twine fallback documented in
   docs/retro/project-review-2026-07-09.md §(e)1. Nothing for gen-2 to do but watch it and
   verify the release artifacts once the tag lands.
2. **PyPI follow-through** — once published: add the PyPI badge and `pip install cfgdiff`
   docs to README, verify `pip install cfgdiff` from a clean venv.
3. **Revisit the 4 documented-divergence xfails** in tests/test_dotenv_differential.py if
   the .env policy ever evolves (they are deliberate, documented divergences from
   python-dotenv — do not "fix" them casually).
4. **Prior-art survey** (the A4 gap from the self-review): we verified the PyPI name was
   free but never did an exhaustive prior-art pass (dyff, jd are single-format; something
   closer may exist). Honest gap.
5. **INI round-trip fidelity** — INI emission is not implemented (convert targets are
   yaml/json/toml); assess whether it is worth adding.
6. **Possible `cfgdiff patch` / `cfgdiff set` subcommand** — apply a diff or set a dotted
   path; natural extension, unvalidated demand.

## Order-state note (read this before trusting the inbox)

`control/inbox.md` says `status: new` on every order forever — one-writer rule, the
manager's status flips lag. **`control/status.md` `orders: done=` is the source of truth**
for what is complete. At wind-down: acked/done = 001, 002, 003, 004.
