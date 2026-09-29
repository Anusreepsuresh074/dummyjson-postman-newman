#!/usr/bin/env bash
# Fails if a report contains the test user's password or anything shaped like a JWT.
#
# Usage: scripts/check-secrets.sh [reports dir]   (default: reports/)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="${1:-$root/reports}"
if [[ ! -e "$target" ]]; then
  echo "Nothing to check: $target does not exist" >&2
  exit 2
fi

if [[ -f "$root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$root/.env"
  set +a
fi

found=0
if [[ -n "${AUTH_PASSWORD:-}" ]] && grep -rqF -- "$AUTH_PASSWORD" "$target"; then
  echo "LEAK: the test user's password appears in $target" >&2
  found=1
fi
if grep -rqE 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.' "$target"; then
  echo "LEAK: a JWT appears in $target" >&2
  found=1
fi

if [[ "$found" -eq 0 ]]; then
  echo "Secret check: no password or token found in $target"
fi
exit "$found"
