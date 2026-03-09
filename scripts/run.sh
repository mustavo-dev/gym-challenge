#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

cmd="${1:-run}"
case "$cmd" in
  run)
    python3 src/main.py
    ;;
  test)
    PYTHONPATH=src python3 -m unittest discover -s tests -q
    ;;
  *)
    echo "Usage: $0 [run|test]"
    exit 2
    ;;
esac

