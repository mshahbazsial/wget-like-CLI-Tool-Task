#!/usr/bin/env python3
import argparse
import os
import sys
import urllib.error
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPRedirectHandler

CHUNK_SIZE = 64 * 1024


class VerboseRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print(f'Redirect: {code} -> {newurl}')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def derive_name(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.rstrip('/')) or 'index.html'


def main() -> int:
    parser = argparse.ArgumentParser(description='Stage 5 - Redirect handling and error reporting')
    parser.add_argument('url')
    parser.add_argument('-o', '--output')
    args = parser.parse_args()

    out_name = args.output or derive_name(args.url)
    opener = build_opener(VerboseRedirectHandler)
    try:
        with opener.open(args.url) as response, open(out_name, 'wb') as f:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
        print(f'Saved to {out_name}')
        return 0
    except urllib.error.HTTPError as e:
        body = e.read(200).decode('utf-8', errors='replace')
        print(f'HTTP error: {e.code} {e.reason}', file=sys.stderr)
        if body:
            print(body, file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f'Network error: {e.reason}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
