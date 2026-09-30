#!/usr/bin/env python3
"""Fetch and verify locked inputs; reuse verified local archives without network access."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
def fetch(entries, offline=False):
    (ROOT / 'sources').mkdir(exist_ok=True)
    for entry in entries:
        target = ROOT / 'sources' / entry['file']
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Checksum mismatch: ' + str(target))
            continue
        if offline:
            raise ValueError('Offline source missing: ' + str(target))
        temporary = target.with_suffix('.download')
        try:
            with urllib.request.urlopen(entry['url'], timeout=120) as response:
                temporary.write_bytes(response.read())
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Downloaded checksum mismatch: ' + entry['file'])
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        print('Verified ' + entry['file'], flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('versions', nargs='*')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    versions = json.loads((ROOT / 'versions.json').read_text())['versions']
    selected = set(args.versions) | {'1.20.4'}
    unknown = selected - {v['version'] for v in versions}
    if unknown:
        parser.error('Unknown versions: ' + ', '.join(sorted(unknown)))
    inputs = json.loads((ROOT / 'sources.lock.json').read_text())['sources']
    inputs += [v for v in versions if args.all or v['version'] in selected]
    fetch(inputs, args.offline)
