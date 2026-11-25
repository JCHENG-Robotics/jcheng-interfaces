#!/usr/bin/env bash
# Build and test jcheng-interfaces in the laptop ROS 2 Humble container.
#
# Mirrors the m2-contract CI job: ros:humble-ros-base, build only
# jcheng_interfaces, then the contract checks with pytest>=8 and
# jsonschema>=4 (both from /opt/jcheng/venv, because Ubuntu 22.04's apt
# versions are older than pyproject.toml requires).
#
#   scripts/humble_ci.sh
#
# The build runs in a disposable copy of the repository, so the host checkout
# keeps no Humble build/install artifacts. CI remains the artifact authority.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-armpi-humble-moveit:latest}"

usage() {
    sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

case "${1:-}" in
    '') ;;
    -h|--help|help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
esac

docker info >/dev/null 2>&1 || { echo "FAIL: cannot access the Docker daemon" >&2; exit 1; }

inner=$(cat <<'INNER'
set -e
source /opt/ros/humble/setup.bash

rm -rf /tmp/repo
cp -a /repo/. /tmp/repo/
rm -rf /tmp/repo/build /tmp/repo/install /tmp/repo/log
cd /tmp/repo

colcon build --base-paths ros2_ws/src --packages-select jcheng_interfaces \
    --event-handlers console_cohesion+
source install/setup.bash
source /opt/jcheng/venv/bin/activate

python3 tools/generate_manifest.py --check
python3 tools/check_schemas.py
python3 tools/check_no_hardware.py
python3 -m pytest -q
ros2 interface show jcheng_interfaces/msg/MotionCommand >/dev/null
INNER
)

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$REPO_ROOT":/repo:ro \
    -w /repo \
    "$IMAGE" bash -lc "$inner"
