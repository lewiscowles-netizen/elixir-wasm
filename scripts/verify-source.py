#!/usr/bin/env python3
"""Verify downloaded archives before any source extraction."""
import hashlib
import json
from pathlib import Path
import sys

entries = json.loads(Path('/builder/sources.lock.json').read_text())['sources'] + json.loads(Path('/builder/versions.json').read_text())['versions']
by_file = {entry['file']: entry for entry in entries}
for name in sys.argv[1:]:
    entry = by_file[name]
    actual = hashlib.sha256((Path('/sources') / name).read_bytes()).hexdigest()
    if actual != entry['sha256']:
        raise SystemExit('Source checksum mismatch: ' + name)
    print('Verified ' + name)
