#!/usr/bin/env python3
import argparse
import os
import sys
import time
import urllib.error
from urllib.parse import urlparse
from urllib.request import urlopen

CHUNK_SIZE = 64 * 1024


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def download(url: str, out_name: str, timeout: float) -> None:
    with urlopen(url, timeout=timeout) as response, open(out_name, 'wb') as f:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 6 - Retry logic and timeout')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    parser.add_argument('--retry', type=int, default=3, help='Number of retries after the first attempt')
    parser.add_argument('--timeout', type=float, default=10.0, help='Socket timeout in seconds')
    parser.add_argument('--wait', type=float, default=1.0, help='Sleep between retries')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    attempts = args.retry + 1
    for attempt in range(1, attempts + 1):
        try:
            print(f'Attempt {attempt}/{attempts}...')
            download(args.url, out_name, args.timeout)
            print(f'Saved to {out_name}')
            return 0
        except Exception as e:
            print(f'Attempt {attempt} failed: {e}', file=sys.stderr)
            if attempt == attempts:
                return 1
            time.sleep(args.wait)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
