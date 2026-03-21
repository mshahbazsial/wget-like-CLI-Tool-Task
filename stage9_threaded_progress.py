#!/usr/bin/env python3
import argparse
import os
import sys
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import urlopen

BUF_SIZE = 1024 * 1024  # 1 MB


@dataclass
class State:
    done: int = 0
    total: int | None = None
    started: float = time.time()
    finished: bool = False
    error: str | None = None


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def human_bytes(value: float) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    idx = 0
    while value >= 1024 and idx < len(units) - 1:
        value /= 1024.0
        idx += 1
    return f'{value:.2f} {units[idx]}'


def downloader(url: str, out_name: str, state: State) -> None:
    try:
        with urlopen(url) as response, open(out_name, 'wb') as f:
            total = response.headers.get('Content-Length')
            state.total = int(total) if total and total.isdigit() else None
            state.started = time.time()
            while True:
                chunk = response.read(BUF_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                state.done += len(chunk)
    except Exception as e:
        state.error = str(e)
    finally:
        state.finished = True


def progress_worker(state: State) -> None:
    while not state.finished:
        elapsed = max(time.time() - state.started, 1e-6)
        speed = state.done / elapsed
        if state.total:
            pct = state.done / state.total * 100
            left = state.total - state.done
            eta = left / speed if speed > 0 else 0
            line = (
                f'\r{pct:6.2f}% done={human_bytes(state.done)} left={human_bytes(left)} '
                f'speed={human_bytes(speed)}/s eta={eta:5.1f}s'
            )
        else:
            line = f'\rdone={human_bytes(state.done)} speed={human_bytes(speed)}/s'
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.1)
    elapsed = max(time.time() - state.started, 1e-6)
    speed = state.done / elapsed
    sys.stdout.write(f'\r100.00% done={human_bytes(state.done)} speed={human_bytes(speed)}/s                    \n')
    sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 9 - Threaded progress reporting')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    state = State()
    t1 = threading.Thread(target=downloader, args=(args.url, out_name, state), daemon=True)
    t2 = threading.Thread(target=progress_worker, args=(state,), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    if state.error:
        print(f'Error: {state.error}', file=sys.stderr)
        return 1
    print(f'Saved to {out_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
