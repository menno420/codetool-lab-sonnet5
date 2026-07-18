# codetool-lab-sonnet5 · status
updated: 2026-07-09T20:02:14Z
phase: wind-down complete — ready for archive + fresh session
health: green
last-shipped: #15 — succession: wind-down pack (whole-life review, NEXT-BOOT guide, proposed gen-2 custom instructions, tested env spec + setup script, gen-2 blueprint feedback), squash-merged to main at a28f7d3. Also this session: #14 — PING-ACK ORDER 004 (discovered 2026-07-09T19:53:36Z via session-start inbox read, acked before all other wind-down work).
blockers: none
orders: acked=001,002,003,004 done=001,002,003,004
⚑ needs-owner:
  1. [2 min, biggest payoff] Register the PyPI trusted publisher: pypi.org → Publishing →
     "Add a pending publisher" with owner `menno420`, repository `codetool-lab-sonnet5`,
     workflow `release.yml`, environment `pypi`. Click-by-click steps in
     docs/retro/project-review-2026-07-09.md §(e)3.
  2. Release 0.1.1 with one push:
     `git tag -a v0.1.1 0b1eb60 -m "cfgdiff 0.1.1" && git push origin v0.1.1`
     — runs the test gate, builds sdist+wheel, cuts the GitHub release with the CHANGELOG
     0.1.1 section as body, and (if item 1 is done first) publishes to PyPI. Do NOT tag
     v0.1.0 at 0260aae expecting automation — it predates release.yml and would fire nothing.
  3. Optional, cosmetic: delete leftover probe branch `test/push-check` (agents get
     HTTP 403 on branch deletes).
notes: |
  Gen-1 ends here, deliberately and in order. The tool is real: cfgdiff 0.1.1 is on main,
  independently verified, 165 tests + 4 deliberate xfails, CI green across 3 Python
  versions, installable today by any stranger via
  `pipx install git+https://github.com/menno420/codetool-lab-sonnet5`; PyPI is one owner
  click plus one tag push away. Everything the next session needs survives in git:
  docs/succession/ (start at NEXT-BOOT.md) and docs/retro/winddown-review-2026-07-09.md
  carry the queue, the walls with exact error text, and the lessons — the biggest being
  that a differential oracle found 3 real bugs behind 114 green tests, and that the
  platform's silent failure modes (dead-at-setup vs not-yet-woken, indistinguishable)
  cost more wall-clock than every loud error combined. The fleet gen-2 blueprint was
  reachable at wind-down and this lane's experience largely confirms it; disagreements
  and additions are in docs/succession/GEN2-FEEDBACK.md. Honest residue: release.yml has
  never actually fired — it triggers on a `v*` tag push, and direct git tag-push 403s from an
  agent seat (the fleet-proven fix is to add a `workflow_dispatch` trigger and dispatch it
  agent-side, as codetool-lab-opus4.8's release.yml does; or the owner pushes the tag). The
  PyPI publish itself still needs the owner (trusted-publisher registration + token). Its
  first real run is item 2 above.
  Good night, gen-1.
