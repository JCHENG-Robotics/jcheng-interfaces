#!/usr/bin/env bash
# Build and test jcheng-interfaces with the host ROS 2 Jazzy toolchain.
#
# Mirrors the m2-contract CI job (ros:jazzy-ros-base): build only
# jcheng_interfaces, then run the contract checks.
#
#   scripts/jazzy_ci.sh
#
# The build runs in a disposable copy of the repository, so the checkout keeps
# no build/install/log artifacts. CI remains the artifact authority.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_SETUP="${ROS_SETUP:-/opt/ros/jazzy/setup.bash}"

usage() {
    sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
    '') ;;
    -h|--help|help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
esac

[[ -f "$ROS_SETUP" ]] || { echo "FAIL: missing ROS setup: $ROS_SETUP" >&2; exit 1; }
command -v colcon >/dev/null 2>&1 || { echo "FAIL: colcon is not on PATH" >&2; exit 1; }
python3 -c 'import pytest, yaml, jsonschema' 2>/dev/null || {
    echo "FAIL: host Python lacks pytest/PyYAML/jsonschema" >&2
    exit 1
}

WORK="$(mktemp -d "${TMPDIR:-/tmp}/jcheng-interfaces-jazzy.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
tar -C "$REPO_ROOT" -cf - \
    --exclude=.git --exclude=.worktrees --exclude=build --exclude=install --exclude=log \
    . | tar -C "$WORK" -xf -
cd "$WORK"

# ROS setup scripts reference optional variables (COLCON_TRACE, etc.), so keep
# `-u` off for the rest of the script.
set +u
# shellcheck disable=SC1090
source "$ROS_SETUP"

colcon build --base-paths ros2_ws/src --packages-select jcheng_interfaces \
    --event-handlers console_cohesion+
# shellcheck disable=SC1091
source install/setup.bash

python3 tools/generate_manifest.py --check
python3 tools/check_schemas.py
python3 tools/check_no_hardware.py
python3 -m pytest -q
ros2 interface show jcheng_interfaces/msg/MotionCommand >/dev/null
