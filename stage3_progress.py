#!/usr/bin/env python3
import argparse
import os
import sys
from urllib.parse import urlparse
from urllib.request import urlopen

CHUNK_SIZE = 64 * 1024


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def progress_bar(done: int, total: int | None, width: int = 30) -> str:
    if total and total > 0:
        filled = int(width * done / total)
        pct = done / total * 100
        left = total - done
        return f"[{'#' * filled}{'-' * (width - filled)}] {pct:6.2f}% {done}/{total} bytes left={left}"
    return f'[streaming] {done} bytes received'


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 3 - Progress bar')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
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
            sys.stdout.write('\r' + progress_bar(done, total_int))
            sys.stdout.flush()
    print(f'\nSaved to {out_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
