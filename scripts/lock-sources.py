#!/usr/bin/env python3
"""Refresh first/latest stable source pins from the recorded tag discovery input."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
def download(entry, previous=None):
    target = ROOT / 'sources' / entry['file']
    target.parent.mkdir(exist_ok=True)
    expected = previous['sha256'] if previous and previous['url'] == entry['url'] else None
    if target.exists() and expected:
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Cached source differs from its existing lock: ' + str(target))
    else:
        temporary = target.with_suffix('.download')
        try:
            with urllib.request.urlopen(entry['url'], timeout=90) as response:
                temporary.write_bytes(response.read())
            if expected and hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
                raise ValueError('Upstream source differs from its existing lock: ' + entry['url'])
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    entry['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    print(entry['file'], flush=True)
    return entry

def main():
    previous = {}
    for filename, field in [('versions.json', 'versions'), ('sources.lock.json', 'sources')]:
        if (ROOT / filename).exists():
            previous.update({entry['file']: entry for entry in json.loads((ROOT / filename).read_text())[field]})
    with urllib.request.urlopen('https://api.github.com/repos/elixir-lang/elixir/git/matching-refs/tags/v', timeout=90) as response:
        discovered = json.load(response)
    import re
    tags = [entry for entry in discovered if re.fullmatch(r'refs/tags/v[1-9]\d*\.\d+\.\d+', entry['ref'])]
    groups = {}
    for tag in tags:
        version = tag['ref'].split('/v')[1]
        groups.setdefault('.'.join(version.split('.')[:2]), []).append(version)
    entries = []
    for series, versions in sorted(groups.items(), key=lambda item: tuple(map(int, item[0].split('.')))):
        versions.sort(key=lambda v: tuple(map(int, v.split('.'))))
        for version in dict.fromkeys([versions[0], versions[-1]]):
            entries.append({'version': version, 'series': series, 'position': 'first' if version == versions[0] else 'latest', 'file': f'elixir-{version}.tar.gz', 'url': f'https://codeload.github.com/elixir-lang/elixir/tar.gz/refs/tags/v{version}'})
    sources = [
        {'name': 'otp', 'version': '29.0.6', 'commit': 'e07fd07837e5aa845657f5fa340637121e451d47', 'file': 'otp.tar.gz', 'url': 'https://codeload.github.com/erlang/otp/tar.gz/e07fd07837e5aa845657f5fa340637121e451d47'},
        {'name': 'popcorn', 'version': '0.4.0-next.0', 'commit': 'bea24dd50fec39a5859e49c54d496736a3c6857a', 'file': 'popcorn.tar.gz', 'url': 'https://codeload.github.com/software-mansion/popcorn/tar.gz/bea24dd50fec39a5859e49c54d496736a3c6857a'},
        {'name': 'autoconf', 'version': '2.72', 'file': 'autoconf.tar.gz', 'url': 'https://ftp.gnu.org/gnu/autoconf/autoconf-2.72.tar.gz'},
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        entries = list(pool.map(lambda entry: download(entry, previous.get(entry['file'])), entries))
        sources = list(pool.map(lambda entry: download(entry, previous.get(entry['file'])), sources))
    (ROOT / 'versions.json').write_text(json.dumps({'schemaVersion': 1, 'asOf': __import__('datetime').date.today().isoformat(), 'policy': 'first and latest stable patch of every released minor, starting at 1.0; prereleases and moving latest tags excluded', 'versions': entries}, indent=2) + '\n')
    (ROOT / 'sources.lock.json').write_text(json.dumps({'schemaVersion': 1, 'sources': sources, 'images': {'emsdk': 'emscripten/emsdk:6.0.2@sha256:644883f58ca15c38c8be59b3a727ba0eff347729bc31d50a3348a6c9ed92bc07', 'otp': 'hexpm/erlang:29.0.6-ubuntu-noble-20260911@sha256:7bc4f2c3eea8acec1d27572f85c22c55c50d7def5b9790ea7c94c7ff93cf6e78'}}, indent=2) + '\n')

if __name__ == '__main__':
    main()
