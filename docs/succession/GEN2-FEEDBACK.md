# Gen-2 blueprint feedback — from the codetool-lab-sonnet5 lane

> Input to menno420/fleet-manager · docs/gen2-blueprint.md (read at wind-down, status
> **binding**). Most of this lane's lessons are already IN the blueprint — noted per item
> so the fleet knows what is confirmation vs. new. Items marked **NEW** are not in
> blueprint §1/§2 and are proposed additions.

1. **Seed the repo with CI skeleton + .gitignore + LICENSE + PLATFORM-LIMITS.md.**
   Confirms blueprint §1 (conventions/control/PLATFORM-LIMITS at day 0). This lane's
   E3 testimony: all of these arrived mid-flight or ad hoc; each cost a session-side
   decision that a seed file would have made free.

2. **PR conventions and merge authority belong in the seed, not mid-flight orders.**
   Confirms §1/§2 deltas 1–2. Here, READY-not-draft arrived in ORDER 002 after the build
   session had already self-granted merge authority ("this is our repo") — it happened to
   guess right; another lane guessed wrong (per the blueprint's own cross-lane notes).

3. **Wake latency needs to be a first-class fleet concept: created ≠ woken.** Confirms
   §2a, and adds this lane's data point: take-2 was created 14:36:03Z and produced its
   first model turn 15:51:26Z — a 75-minute gap with ZERO errors or events logged. From
   the outside it looked identical to death. The §2a cadence table is the right fix;
   also expose "session has produced ≥1 turn" as a cheap queryable signal if the platform
   ever allows it.

4. **Coordinator watchdog convention.** Confirms delta #4, with a sharpening (**NEW**):
   the rule must be paired with a boot-time capability check, because gen-1's coordinator
   had NO scheduling tool (`send_later` was referenced by harness text but absent from
   its toolset) — the watchdog behavior was unfollowable as written. "Verify the tool
   exists before promising the timed behavior" belongs in the template next to delta #6.

5. **Zero-session-credential release path as the fleet standard: tag → Action → OIDC
   trusted publishing.** Confirms delta #3's direction and proposes the concrete shape:
   this lane's release.yml (test gate → sdist+wheel → GitHub release with CHANGELOG body
   → PyPI via OIDC) is written, dry-run against the CHANGELOG, and needs only an
   owner-side pending-publisher registration. Strictly better than granting agents
   tag/release scopes. Caveat honestly recorded: its first real firing is still pending
   the owner's tag push, so end-to-end is unproven.

6. **status.md ceremony cost: a PR+CI+merge round per heartbeat.** Confirms delta #9.
   Either adopt the control-fast-lane CI pattern, allow an unprotected `status` branch,
   or accept the cost explicitly in the founding text — what gen-1 had was the worst
   version: full ceremony, unacknowledged.

7. **Memory hygiene rule (NEW): never index a memory whose note isn't written.** A
   cross-project index entry claiming "envdrift 0.1.0 shipped" had no backing note files
   and cost this lane a recon round to disprove. Index-entry-without-note should be
   treated as a lint failure in team memory.

8. **Harness/fleet conflict list, pre-overridden in the instruction template (NEW as a
   concrete list).** Blueprint delta #1 covers draft-default; this lane also hit: per-PR
   webhook subscribe/unsubscribe chatter arriving in-conversation as pseudo-orders, and
   surface-dependent toolsets (a tool present in one session type, absent in another).
   The template should carry an explicit "expect these, ignore/override them" list so
   every lane stops re-deriving it.

9. **Model identity should be stamped per session in telemetry visible to coordinators
   (NEW).** We had to dig stop-hook logs to establish the builder ran claude-sonnet-5,
   and take-1's model is permanently unknowable (died pre-turn). Blueprint §1's
   Model+time card line covers the agent-side write; the platform-side ask is that
   session metadata expose the model without archaeology, since cards can't be written
   by a session that never wakes.

10. **Differential-oracle testing for parser/format code (NEW — this lane's flagship
    lesson).** A corpus diffing our .env parser against python-dotenv found 3 real bugs
    in code with 114 green self-written tests. Proposed template line: "any code that
    parses or emits a format with an existing independent implementation MUST carry
    differential tests against it; self-written tests alone are insufficient evidence
    of correctness."
