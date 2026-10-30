#!/usr/bin/env bash
# Launch the Stage 1 pilot detached in tmux on auxo. Log: runs/<name>.log
# Usage: ./run_pilot.sh pilot1
set -euo pipefail
NAME="${1:?run name}"
HERE="$(cd "$(dirname "$0")" && pwd)"
KEYFILE="$HOME/.config/anthropic/api_key"   # chmod 600; never inside the repo
if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -r "$KEYFILE" ]; then ANTHROPIC_API_KEY="$(tr -d "[:space:]" < "$KEYFILE")"; fi
: "${ANTHROPIC_API_KEY:?set ANTHROPIC_API_KEY or put the key in $KEYFILE}"
mkdir -p "$HERE/runs"
LOG="$HERE/runs/$NAME.log"
tmux new-session -d -s "stage1_$NAME" -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  "cd '$HERE/scripts' && { uv run python build_dataset.py --run-dir ../runs/$NAME \
   && uv run python make_review.py ../runs/$NAME; echo EXIT=\$?; } >> '$LOG' 2>&1"
echo "started tmux session stage1_$NAME; tail -f $LOG"
