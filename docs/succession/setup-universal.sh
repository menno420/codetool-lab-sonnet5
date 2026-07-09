#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup-universal.sh — defensive environment setup for codetool-lab (gen-2)
#
# Adapted from the fleet canonical template:
#   menno420/fleet-manager · environments/templates/setup-universal.sh
# (reachable at gen-1 wind-down; adopted with lane-specific additions:
#  pyproject [project] editable install with [dev] extra, requirements*.txt
#  glob, and non-fatal tooling preinstall).
#
# CONTRACT (fleet playbook R15): this script NEVER fails the session.
# Gen-1's take-1 session died at setup with zero model turns because the
# script assumed requirements.txt existed ("Could not open requirements
# file"). A failing setup script = dead session, no signal. Every step below
# is best-effort and the script ALWAYS exits 0. Worst case is a session with
# missing deps that can still report and self-repair; that beats no session.
# ---------------------------------------------------------------------------

# Defensive posture: no set -e (a failing step must not abort), no set -u
# (unset vars tolerated), no pipefail.
set +e

log() { echo "[env-setup] $*"; }

setup_one() {
  repo_dir="$1"
  name="$(basename "$repo_dir")"

  # 1. Repo-provided script wins (the repo knows best).
  if [ -f "$repo_dir/scripts/env-setup.sh" ]; then
    log "$name: running scripts/env-setup.sh"
    ( cd "$repo_dir" && bash scripts/env-setup.sh ) \
      || log "$name: env-setup.sh failed (non-fatal, continuing)"
    return 0
  fi

  # 2. Any requirements*.txt that actually exists (never assume one does).
  found_reqs=0
  for req in "$repo_dir"/requirements*.txt; do
    [ -f "$req" ] || continue
    found_reqs=1
    log "$name: pip install -r $(basename "$req")"
    ( cd "$repo_dir" && python3 -m pip install --quiet -r "$req" ) \
      || log "$name: pip install -r $(basename "$req") failed (non-fatal)"
  done

  # 3. pyproject.toml with a [project] table -> editable install, dev extra
  #    preferred, plain fallback, both non-fatal.
  if [ -f "$repo_dir/pyproject.toml" ] && grep -q '^\[project\]' "$repo_dir/pyproject.toml" 2>/dev/null; then
    log "$name: pip install -e '.[dev]' (fallback: -e .)"
    ( cd "$repo_dir" && python3 -m pip install --quiet -e '.[dev]' ) \
      || ( cd "$repo_dir" && python3 -m pip install --quiet -e . ) \
      || log "$name: editable install failed (non-fatal, continuing)"
  elif [ "$found_reqs" -eq 0 ]; then
    log "$name: no scripts/env-setup.sh, requirements*.txt, or [project] pyproject — skipping (docs-only repo is fine)"
  fi
}

# Tooling preinstall, non-fatal (gen-1's build session installed all of this
# by hand; preinstalling saves the first-turn tax without risking the boot).
log "preinstalling common tooling (best-effort)"
python3 -m pip install --quiet build pytest ruff || log "tooling preinstall failed (non-fatal)"

# Multi-repo workspace vs single-repo detection.
if [ -d .git ]; then
  setup_one "$PWD"
else
  found=0
  for d in */; do
    [ -d "$d/.git" ] || continue
    found=1
    setup_one "$PWD/${d%/}"
  done
  # Nothing looked like a git clone: best-effort pass on the cwd itself.
  [ "$found" -eq 1 ] || setup_one "$PWD"
fi

# The single most important line in the file (R15). Do not "improve" this.
log "setup complete (defensive shim: always exit 0)"
exit 0
