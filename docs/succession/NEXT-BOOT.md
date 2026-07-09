# NEXT-BOOT — gen-2 session, your first 10 minutes

You are a fresh session inheriting codetool-lab-sonnet5 (cfgdiff). Nothing from your
predecessor's chat context survives; everything you need is in this repo. Do the three
sections below in order.

## 1. READ ORDER

1. `control/README.md` — the coordination protocol and the one-writer rule; everything
   else assumes you know it.
2. `control/inbox.md` — your orders. **Note: every order says `status: new` forever** —
   the manager's status flips lag. Diff the inbox against status.md's `orders: done=` line
   to see what is actually outstanding.
3. `control/status.md` — the source of truth for what is done, plus the ⚑ needs-owner
   ledger (things only the owner can click).
4. `docs/succession/README.md` — queue state: DONE / IN-FLIGHT / NEXT.
5. **KNOWN WALLS, section 3 below** — read before you plan anything involving tags,
   releases, or branch deletion. Probing a documented wall twice is a bug.
6. `README.md` + `CHANGELOG.md` — what cfgdiff is and the current version (0.1.1,
   unreleased pending an owner tag push).
7. `docs/retro/winddown-review-2026-07-09.md` — the whole life story; read only when you
   need context beyond the above, not as a boot gate.

## 2. WALKING-SKELETON CHECK — prove the loop before real work

Prove branch → PR → CI → merge end-to-end before touching anything that matters:

1. `git checkout -b skeleton/boot-check`
2. Touch a heartbeat change in `control/status.md`: update the `updated:` timestamp
   (from `date -u`, never your sense of time) and add a "gen-2 boot" note line.
3. `git push -u origin skeleton/boot-check`
4. Open a **READY** PR (the harness will suggest a draft — refuse; fleet convention is
   READY, never draft).
5. Confirm `ci.yml` goes green on the PR.
6. Squash-merge it yourself — self-merge on green is granted by convention (ORDER 002).

If any step fails, **that failure is your first ⚑ item, not a reason to stop** — record
the exact error text, flag it, and keep working around it.

## 3. KNOWN WALLS — exact error text; never re-probe

- **Tag push and branch delete → HTTP 403 at the git proxy.** Both
  `git push origin v0.1.0` and `git push origin --delete test/push-check` fail verbatim:
  ```
  error: RPC failed; HTTP 403 curl 22 The requested URL returned error: 403
  send-pack: unexpected disconnect while reading sideband packet
  fatal: the remote end hung up unexpectedly
  ```
  Tags and branch deletion are owner-only. Do not probe again.
- **github MCP has no release/tag creation tools** — only read-only ones (list_releases,
  get_latest_release, get_release_by_tag, get_tag, list_tags). You cannot cut a release
  from a session.
- **Direct api.github.com is blocked**: "GitHub access is not enabled for this session".
  The github MCP server is your only GitHub write surface.
- **Draft PRs are forbidden by fleet convention** — the harness will still suggest them
  on every PR. Always create READY.
- **PyPI publishing needs the owner-side trusted-publisher registration** (pypi.org →
  Publishing → pending publisher: owner `menno420`, repo `codetool-lab-sonnet5`, workflow
  `release.yml`, environment `pypi`). After that, `.github/workflows/release.yml` handles
  everything on a tag push — no session credential exists or is needed.
- **Main is PR-gated, but self-merge on green is granted** by standing convention
  (ORDER 002). You do not need to ask permission to merge your own green PR.

## 4. FIRST REAL ACTIONS

1. Read the inbox for orders newer than 004 (the last order gen-1 completed). If found,
   they win.
2. If none: work the NEXT queue in `docs/succession/README.md`, top to bottom (watch for
   the v0.1.1 tag/release having fired; verify and document it if so).
3. End every session by overwriting `control/status.md` (via READY PR, self-merged on
   green) — the heartbeat is how you exist to the fleet.
