#!/usr/bin/env bash
# M1 gate for jcheng-interfaces.
# M1 must not define IDL, packages or a license. The contract audit comes first.

set -euo pipefail

fail=0
require_file() {
  if [[ ! -f "$1" ]]; then
    echo "MISSING: $1" >&2
    fail=1
  fi
}

for f in \
  README.md \
  VERSION \
  CHANGELOG.md \
  LICENSE-REVIEW.md \
  docs/M1-SCOPE.md \
  docs/CONTRACT_AUDIT_PLAN.md \
  docs/CONTRACT.md \
  docs/VERSIONING.md \
  docs/COMPATIBILITY.md \
  .github/workflows/ci.yml \
  .github/CODEOWNERS
do
  require_file "$f"
done

if [[ -e LICENSE ]]; then
  echo "ERROR: LICENSE must not exist before the license review is approved." >&2
  fail=1
fi

found_idl="$(find ros2_ws schemas -type f \( -name '*.msg' -o -name '*.srv' -o -name '*.action' \) -print -quit 2>/dev/null || true)"
if [[ -n "${found_idl}" ]]; then
  echo "ERROR: IDL found before the contract audit is approved: ${found_idl}" >&2
  fail=1
fi

found_pkg="$(find . -path ./.git -prune -o -name 'package.xml' -print -quit | grep . || true)"
if [[ -n "${found_pkg}" ]]; then
  echo "ERROR: package.xml found; M1 must not create a ROS package." >&2
  fail=1
fi

found_py="$(find . -path ./.git -prune -o -type f -name '*.py' -print -quit | grep . || true)"
if [[ -n "${found_py}" ]]; then
  echo "ERROR: Python source found; M1 must not create bindings." >&2
  fail=1
fi

if grep -RIlE \
  --exclude-dir=.git \
  --exclude='check_m1_gate.sh' \
  'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' \
  . >/dev/null 2>&1; then
  echo "ERROR: possible secret material found." >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "M1 interfaces gate FAILED" >&2
  exit 1
fi
echo "M1 interfaces gate OK (no IDL, no package, no LICENSE)"
