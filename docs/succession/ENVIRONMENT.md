# Environment spec — codetool-lab (gen-2)

## Setup script

Use [setup-universal.sh](setup-universal.sh) (paste into claude.ai/code → Environments →
setup script). It is adapted from the fleet's canonical template
(menno420/fleet-manager · environments/templates/setup-universal.sh — reachable and read
at gen-1 wind-down), with lane-specific additions: pyproject `[project]` editable install
with `[dev]` extra, `requirements*.txt` glob instead of assuming one file, and non-fatal
preinstall of `build`, `pytest`, `ruff`.

**Contract: the script never fails the session — it always exits 0.** Gen-1's take-1
session died at setup with zero model turns because the then-current script assumed
requirements.txt existed. A session with missing deps can report and self-repair; a dead
session cannot.

Tested in this container at wind-down (2026-07-09):

- from the repo root: exits 0, installs cfgdiff editable with dev extras;
- from a non-repo cwd: exits 0, skips gracefully.

## Environment variables (NAMES only — never values in git)

**Required: none.** This lane needs no secrets. The release path is tag-push →
`release.yml` → PyPI **trusted publishing** (OIDC): no session ever holds a credential,
and the only setup is the owner-side one-time pending-publisher registration on pypi.org
(owner `menno420`, repo `codetool-lab-sonnet5`, workflow `release.yml`, environment
`pypi`).

**Optional:**

- `PYPI_API_TOKEN` — only for the manual `twine upload` fallback path
  (docs/retro/project-review-2026-07-09.md §(e)1). Prefer trusted publishing; do not add
  this token unless the trusted-publisher route is abandoned.

## Notes for whoever provisions the environment

- Python 3.10+ (CI matrix runs 3.10/3.11/3.12).
- No network services, databases, or third-party APIs are needed.
- Do not add ambient credentials from other lanes; gen-1's only memory-related incident
  was cross-project state leaking in.
