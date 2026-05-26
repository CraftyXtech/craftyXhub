#!/bin/bash
# ============================================================
# CraftyxHub Current Events Batch Runner
# ============================================================
# Run from cron to generate time-sensitive news articles.
#
# Run 1: C.W (author_id=2) — 20 breaking/trending topics
# Run 2: S.A (author_id=1) — 20 diplomacy + AI topics
#
# Delay: 90 seconds between articles to avoid rate limits.
# Uses batch_generate.py with progress tracking so already-completed
# topics are skipped on re-runs.
# ============================================================

set -euo pipefail

REPO=/root/craftyXhub
VENV_PYTHON="$REPO/api/venv/bin/python"
SCRIPT="$REPO/api/scripts/batch_generate.py"
LOG_DIR="$REPO/api/scripts/logs"
PROGRESS_FILE="$REPO/api/scripts/.batch_progress_current.json"
ERROR_FILE="$REPO/api/scripts/.batch_errors_current.jsonl"

mkdir -p "$LOG_DIR"

echo "=== Current Events Batch Run $(date) ==="

# ---- C.W: 20 breaking/trending topics (author_id=2) ----
echo "[C.W] Starting batch — 20 topics, author_id=2..."
$VENV_PYTHON $SCRIPT \
    --category current \
    --author-id 2 \
    --start-from 0 \
    --limit 20 \
    --progress-file "$PROGRESS_FILE" \
    --error-file "$ERROR_FILE" \
    --delay-seconds 90 \
    > "$LOG_DIR/cw_$(date +%Y%m%d_%H%M%S).log" 2>&1
echo "[C.W] Done."

# ---- S.A: 20 diplomacy + AI topics (author_id=1) ----
echo "[S.A] Starting batch — 20 topics, author_id=1..."
$VENV_PYTHON $SCRIPT \
    --category current \
    --author-id 1 \
    --start-from 20 \
    --limit 20 \
    --progress-file "$PROGRESS_FILE" \
    --error-file "$ERROR_FILE" \
    --delay-seconds 90 \
    > "$LOG_DIR/sa_$(date +%Y%m%d_%H%M%S).log" 2>&1
echo "[S.A] Done."

echo "=== Batch Complete $(date) ==="
