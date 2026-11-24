#!/usr/bin/env bash
# Repository gate for jcheng-interfaces after the M2 audit sign-off.
# Allows IDL/package files, but only with an approved audit and no runtime code.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

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
  pyproject.toml \
  interface_manifest.json \
  docs/CONTRACT_AUDIT.md \
  docs/M2-SCOPE.md \
  docs/CONTRACT.md \
  docs/VERSIONING.md \
  docs/COMPATIBILITY.md \
  ros2_ws/src/jcheng_interfaces/package.xml \
  ros2_ws/src/jcheng_interfaces/CMakeLists.txt \
  README.zh-CN.md \
  ROADMAP.md \
  ACCEPTANCE.md \
  .github/workflows/ci.yml \
  .github/CODEOWNERS \
  scripts/check_repo_gate.sh
do
  require_file "$f"
done

if [[ -e LICENSE ]]; then
  echo "ERROR: LICENSE must not exist before the license review is approved." >&2
  fail=1
fi

if ! grep -q 'M2.1 审计已签字' docs/CONTRACT_AUDIT.md; then
  echo "ERROR: contract audit is not signed; IDL is not allowed." >&2
  fail=1
fi

idl_count="$(find ros2_ws/src/jcheng_interfaces -type f \( -name '*.msg' -o -name '*.srv' -o -name '*.action' \) | wc -l)"
if [[ "${idl_count}" -lt 20 ]]; then
  echo "ERROR: expected the v0.1 IDL set; found ${idl_count} files." >&2
  fail=1
fi

package_xml="$(find . -path ./.git -prune -o -path ./build -prune -o -path ./install -prune -o -path ./log -prune -o -name package.xml -print | sort)"
if [[ "${package_xml}" != "./ros2_ws/src/jcheng_interfaces/package.xml" ]]; then
  echo "ERROR: unexpected package.xml set:" >&2
  echo "${package_xml}" >&2
  fail=1
fi

runtime_code="$(find ros2_ws/src/jcheng_interfaces -type f \( -name '*.py' -o -name '*.cpp' -o -name '*.hpp' -o -name '*.h' \) -print -quit)"
if [[ -n "${runtime_code}" ]]; then
  echo "ERROR: runtime code found in the interface package: ${runtime_code}" >&2
  fail=1
fi

if grep -RIl --include='*.py' 'rclpy\|rclcpp' ros2_ws/src/jcheng_interfaces >/dev/null 2>&1; then
  echo "ERROR: rclpy/rclcpp reference found in the interface package." >&2
  fail=1
fi

if find . -path ./.git -prune -o -path ./build -prune -o -path ./install -prune -o -path ./log -prune -o -name '*.launch.py' -print -quit | grep -q .; then
  echo "ERROR: launch files are not allowed in jcheng-interfaces." >&2
  fail=1
fi

if ! python3 tools/check_no_hardware.py; then
  fail=1
fi

python3 - <<'PY' || fail=1
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

version = Path("VERSION").read_text(encoding="utf-8").strip()
package = ET.parse("ros2_ws/src/jcheng_interfaces/package.xml").getroot()
package_version = (package.findtext("version") or "").strip()
if version != package_version:
    print(f"ERROR: VERSION {version!r} != package.xml {package_version!r}", file=sys.stderr)
    raise SystemExit(1)
print(f"VERSION matches package.xml: {version}")
PY

if grep -RIlE \
  --exclude-dir=.git \
  --exclude-dir=build \
  --exclude-dir=install \
  --exclude-dir=log \
  --exclude='check_repo_gate.sh' \
  'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' \
  . >/dev/null 2>&1; then
  echo "ERROR: possible secret material found." >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  echo "repository gate FAILED" >&2
  exit 1
fi
echo "repository gate OK: approved audit, ${idl_count} IDL files, no runtime code, no LICENSE"
