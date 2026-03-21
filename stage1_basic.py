#!/usr/bin/env python3
import argparse
import os
from urllib.parse import urlparse
from urllib.request import urlopen


def derive_name(url: str) -> str:
    path = urlparse(url).path
    name = os.path.basename(path.rstrip('/')) or 'index.html'
    return name


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 1 - Basic file download')
    parser.add_argument('url', help='Remote file URL')
    args = parser.parse_args()

    out_name = derive_name(args.url)
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
