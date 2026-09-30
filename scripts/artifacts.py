#!/usr/bin/env python3
"""Package a deterministic virtual filesystem and hash its browser assets."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
from notices import collect

root = Path('/bundle/fs')
out = Path('/artifacts')
out.mkdir(exist_ok=True)
for name in ('beam.mjs', 'beam.emu.mjs', 'beam.wasm'):
    shutil.copyfile(Path('/out/runtimes/core') / name, out / name)
with io.BytesIO() as data:
    with tarfile.open(fileobj=data, mode='w', format=tarfile.USTAR_FORMAT) as archive:
        for path in sorted(root.rglob('*')):
            if not path.is_file():
                continue
            content = path.read_bytes()
            entry = tarfile.TarInfo(path.relative_to(root).as_posix())
            entry.size = len(content)
            entry.mode = 0o644
            archive.addfile(entry, io.BytesIO(content))
    with (out / 'filesystem.tar.gz').open('wb') as target:
        with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as compressed:
            compressed.write(data.getvalue())
shutil.copyfile('/src/selected-elixir/LICENSE', out / 'ELIXIR-LICENSE')
shutil.copyfile('/src/popcorn/LICENSE', out / 'POPCORN-LICENSE')
shutil.copyfile('/src/otp/LICENSE.txt', out / 'OTP-LICENSE')
collect(out)
lock = json.loads(Path('/builder/sources.lock.json').read_text())
versions = json.loads(Path('/builder/versions.json').read_text())
version = sys.argv[1]
manifest = {'schemaVersion': 1, 'elixir': version, 'otp': '29.0.6', 'target': 'browser-emscripten', 'runtime': 'otp-popcorn', 'profile': 'core', 'source': next(v for v in versions['versions'] if v['version'] == version), 'runtimeSources': lock, 'codePaths': ['/lib/' + directory.name + '/ebin' for directory in sorted((root / 'lib').iterdir()) if (directory / 'ebin').is_dir()], 'capabilities': {'eval': True, 'threads': True, 'wasi': False, 'crypto': False, 'nativeSockets': False, 'subprocesses': False, 'dynamicNifs': False, 'filesystem': 'ephemeral MEMFS'}, 'validation': {'browser': 'not-yet-tested'}, 'files': {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'manifest.json'}}
if Path('/bundle/retargeting.json').exists():
    manifest['profile'] = 'historical-retarget'
    manifest['retargeting'] = json.loads(Path('/bundle/retargeting.json').read_text())
if Path('/bundle/project.json').exists():
    manifest['application'] = json.loads(Path('/bundle/project.json').read_text())
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
