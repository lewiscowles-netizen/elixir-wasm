#!/usr/bin/env python3
"""Include compiled project applications and priv files in the browser filesystem."""
import json
from pathlib import Path
import shutil
import sys

app = sys.argv[1]
compiled = Path('/project/_build/prod/lib')
if not (compiled / app / 'ebin' / (app + '.app')).is_file():
    raise SystemExit('Application was not compiled: ' + app)
root = Path('/bundle/fs/lib')
apps = []
for directory in sorted(compiled.iterdir()):
    if not (directory / 'ebin').is_dir():
        continue
    if (root / directory.name).exists():
        raise SystemExit('Project cannot replace runtime library: ' + directory.name)
    apps.append(directory.name)
    for part in ('ebin', 'priv'):
        source = directory / part
        if source.exists():
            shutil.copytree(source, root / directory.name / part, symlinks=False)
Path('/bundle/project.json').write_text(json.dumps({'name': app, 'applications': apps, 'configuration': 'No Mix runtime configuration is injected; configure explicitly before startup.'}))
