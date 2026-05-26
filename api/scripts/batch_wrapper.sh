#!/bin/bash
# Wrapper: runs batch_generate.py and saves output to a log file
# Usage: batch_wrapper.sh <category> <start-from> <limit>
set -e
CAT=$1
START=$2
LIMIT=$3
cd /root/craftyXhub/api
source venv/bin/activate
OUTFILE=/tmp/batch_${CAT}_$(date +%s).log
python3 scripts/batch_generate.py --category "$CAT" --start-from "$START" --limit "$LIMIT" --word-count medium > "$OUTFILE" 2>&1
cat "$OUTFILE"
# Also save progress snapshot
cat scripts/.batch_progress.json | python3 -c 'import json,sys; d=json.load(sys.stdin); c=d["completed"]; ai=sum(1 for x in c if x.startswith("ai:")); w3=sum(1 for x in c if x.startswith("web3:")); print(f"PROGRESS: AI={ai} WEB3={w3}")'
