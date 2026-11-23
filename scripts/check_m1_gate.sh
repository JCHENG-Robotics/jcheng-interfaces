#!/usr/bin/env bash
# Historical entry point. The M2 gate allows IDL after the audit sign-off.
set -euo pipefail
exec bash "$(dirname "$0")/check_repo_gate.sh"
