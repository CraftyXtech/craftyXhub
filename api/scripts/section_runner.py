#!/usr/bin/env python3
"""
Section-based batch runner for remaining AI topics (indices 80+).
Daemonizes and writes status to /tmp/batch_section_status.json.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

API_ROOT = Path('/root/craftyXhub/api')
sys.path.insert(0, str(API_ROOT))

STATUS_FILE = Path('/tmp/batch_section_status.json')
PROGRESS_FILE = API_ROOT / 'scripts' / '.batch_progress.json'

TOTAL_AI_TOPICS = 630
START_FROM = 80


def write_status(status: dict):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_FILE.open('w') as f:
        json.dump(status, f, indent=2)


def count_ai_done() -> int:
    if not PROGRESS_FILE.exists():
        return 0
    try:
        progress = json.loads(PROGRESS_FILE.read_text())
        completed = progress.get('completed', [])
    except Exception:
        return 0
    return sum(1 for e in completed if e.startswith('ai:'))


def daemonize():
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)
    os.chdir('/')
    os.umask(0)
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/tmp/section_runner.log', 'a') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())


def main():
    daemonize()
    print(f'Runner started at {datetime.now(timezone.utc).isoformat()}', flush=True)

    already = count_ai_done()
    remaining = TOTAL_AI_TOPICS - already

    print(f'AI progress: {already}/{TOTAL_AI_TOPICS} ({remaining} remaining)', flush=True)

    if remaining <= 0:
        write_status({
            'progress': f'{already}/{TOTAL_AI_TOPICS}',
            'running': False,
            'updated_at': datetime.now(timezone.utc).isoformat()
        })
        return

    import subprocess
    cmd = [
        sys.executable, 'scripts/batch_generate.py',
        '--category', 'ai',
        '--start-from', str(START_FROM),
        '--word-count', 'medium',
        '--delay-seconds', '90'
    ]

    print(f'Running: {" ".join(cmd)}', flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=str(API_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    while proc.poll() is None:
        time.sleep(15)
        done = count_ai_done()
        write_status({
            'progress': f'{done}/{TOTAL_AI_TOPICS}',
            'remaining': TOTAL_AI_TOPICS - done,
            'running': True,
            'updated_at': datetime.now(timezone.utc).isoformat()
        })

    done = count_ai_done()
    final_remaining = TOTAL_AI_TOPICS - done
    write_status({
        'progress': f'{done}/{TOTAL_AI_TOPICS}',
        'remaining': final_remaining,
        'running': False,
        'updated_at': datetime.now(timezone.utc).isoformat()
    })

    output = proc.stdout.read() if proc.stdout else ''
    print(f'Runner finished. Final: {done}/{TOTAL_AI_TOPICS}. Remaining: {final_remaining}', flush=True)


if __name__ == '__main__':
    main()
