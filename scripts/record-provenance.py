#!/usr/bin/env python3
"""Record the local recipe bytes that produced a runtime, alongside its upstream source pins."""
import hashlib
import json
from pathlib import Path

root = Path('/builder')
target = Path('/artifacts/manifest.json')
manifest = json.loads(target.read_text())
manifest['builderSources'] = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(root.rglob('*')) if path.is_file() and '__pycache__' not in path.parts}
target.write_text(json.dumps(manifest, indent=2) + '\n')
