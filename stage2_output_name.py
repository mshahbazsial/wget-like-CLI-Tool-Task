#!/usr/bin/env python3
import argparse
import os
from urllib.parse import urlparse
from urllib.request import urlopen


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 2 - Output file naming')
    parser.add_argument('url', help='Remote file URL')
    parser.add_argument('-o', '--output', help='Write output to this filename')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    with urlopen(args.url) as response, open(out_name, 'wb') as f:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            f.write(chunk)
    print(f'Downloaded {args.url} -> {out_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
