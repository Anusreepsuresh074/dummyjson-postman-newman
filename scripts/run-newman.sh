#!/usr/bin/env bash
# The one way to run the collection, locally and in CI.
#
# Usage: scripts/run-newman.sh <main|data|defects>
#   main     every functional folder (the gating run)
#   data     the data-driven search folder, one iteration per CSV row
#   defects  the known-defects folder (expected to fail until DummyJSON fixes them)
#
# Credentials come from AUTH_USERNAME / AUTH_PASSWORD (a .env file locally, repository
# secrets in CI) and reach Newman only as --env-var values. Reports go to
# reports/<UTC time>-<mode>/ (HTML, JUnit, the CLI summary and Newman's exit code). The script's
# exit code is Newman's: non-zero if any assertion or script failed.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-main}"

if [[ -f "$root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$root/.env"
  set +a
fi
: "${AUTH_USERNAME:?AUTH_USERNAME is not set (see .env.example)}"
: "${AUTH_PASSWORD:?AUTH_PASSWORD is not set (see .env.example)}"

collection="$root/collections/dummyjson.postman_collection.json"
environment="$root/environments/dummyjson.postman_environment.json"

case "$mode" in
  main)
    run_args=(--folder "01 Auth" --folder "02 Products" --folder "03 Search and categories"
      --folder "04 Product writes" --folder "05 Protected routes")
    title="DummyJSON API tests"
    ;;
  data)
    run_args=(--folder "06 Data-driven search" --iteration-data "$root/data/search-terms.csv")
    title="DummyJSON data-driven search"
    ;;
  defects)
    run_args=(--folder "99 Known defects")
    title="DummyJSON known defects (expected to fail)"
    ;;
  *)
    echo "Unknown mode '$mode'. Use main, data or defects." >&2
    exit 2
    ;;
esac

out="$root/reports/$(date -u +%Y%m%dT%H%M%SZ)-$mode"
mkdir -p "$out"

# DummyJSON resolves to IPv6 and IPv4 addresses. Node 20 tries both but gives each connection
# attempt only 250 ms, so a slow first connection can fail with AggregateError. Allow 2 s.
export NODE_OPTIONS="${NODE_OPTIONS:-} --network-family-autoselection-attempt-timeout=2000"

set +e
npx --no-install newman run "$collection" \
  --color off \
  --environment "$environment" \
  "${run_args[@]}" \
  --env-var "username=$AUTH_USERNAME" \
  --env-var "password=$AUTH_PASSWORD" \
  --delay-request 100 \
  --timeout-request 30000 \
  --reporters cli,htmlextra,junit \
  --reporter-htmlextra-export "$out/report.html" \
  --reporter-htmlextra-title "$title" \
  --reporter-htmlextra-browserTitle "$title" \
  --reporter-htmlextra-skipSensitiveData \
  --reporter-junit-export "$out/junit.xml" | tee "$out/cli.txt"
status="${PIPESTATUS[0]}" # Newman's exit code, not tee's
set -e

echo "$mode" >"$out/mode"
echo "$status" >"$out/exit-code"
echo "REPORT_DIR=$out"
exit "$status"
