#!/bin/bash
set -euo pipefail

pids=()

cleanup() {
  echo
  echo "Stopping processes..."

  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done

  # Give them a moment to exit cleanly
  sleep 1

  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  done

  echo "Stopped."
}

trap cleanup INT TERM EXIT

cd frontend
npm run start &
pids+=("$!")

cd ../backend
python -m fastapi main.py &
pids+=("$!")

echo "Started:"
echo "  npm run start          pid=${pids[0]}"
echo "  python -m fastapi main.py pid=${pids[1]}"
echo
echo "Press Ctrl+C to stop both."

# Wait indefinitely until Ctrl+C
while true; do
  sleep 1
done