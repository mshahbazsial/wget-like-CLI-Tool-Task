#!/usr/bin/env python3
import argparse
import base64
import os
import sys
import urllib.error
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CHUNK_SIZE = 64 * 1024


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def parse_headers(header_items: list[str] | None) -> list[tuple[str, str]]:
    headers = []
    for item in header_items or []:
        if ':' not in item:
            raise ValueError(f'Invalid header format: {item!r}. Expected Name: Value')
        name, value = item.split(':', 1)
        headers.append((name.strip(), value.strip()))
    return headers


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 7 - Auth and custom headers')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--header', action='append', help='Custom header, e.g. --header "X-Test: 1"')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    req = Request(args.url)
    for k, v in parse_headers(args.header):
        req.add_header(k, v)
    if args.user is not None:
        token = f'{args.user}:{args.password or ""}'.encode('utf-8')
        req.add_header('Authorization', 'Basic ' + base64.b64encode(token).decode('ascii'))

    try:
        with urlopen(req) as response, open(out_name, 'wb') as f:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
        print(f'Saved to {out_name}')
        return 0
    except urllib.error.HTTPError as e:
        print(f'HTTP error: {e.code} {e.reason}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
