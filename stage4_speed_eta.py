#!/usr/bin/env python3
import argparse
import os
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen

CHUNK_SIZE = 64 * 1024


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


def format_eta(seconds: float | None) -> str:
    if seconds is None:
        return '--:--'
    seconds = max(0, int(seconds))
    return f'{seconds // 60:02d}:{seconds % 60:02d}'


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 4 - Progress + speed + ETA')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    started = time.time()
    with urlopen(args.url) as response, open(out_name, 'wb') as f:
        total = response.headers.get('Content-Length')
        total_int = int(total) if total and total.isdigit() else None
        done = 0
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            elapsed = max(time.time() - started, 1e-6)
            speed = done / elapsed
            eta = ((total_int - done) / speed) if total_int and speed > 0 else None
            if total_int:
                pct = done / total_int * 100
                left = total_int - done
                msg = (
                    f'\r{pct:6.2f}%  got={human_bytes(done)} left={human_bytes(left)} '
                    f'speed={human_bytes(speed)}/s eta={format_eta(eta)}'
                )
            else:
                msg = f'\rgot={human_bytes(done)} speed={human_bytes(speed)}/s eta=--:--'
            sys.stdout.write(msg)
            sys.stdout.flush()
    print(f'\nSaved to {out_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
