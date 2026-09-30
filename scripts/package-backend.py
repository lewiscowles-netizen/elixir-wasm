#!/usr/bin/env python3
"""Package a backend's actual assets with explicit execution capabilities."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

backend, version = sys.argv[1:]
out = Path('/artifacts')
out.mkdir(exist_ok=True)
lock = json.loads(Path('/builder/backends.lock.json').read_text())
source = next(v for v in json.loads(Path('/builder/versions.json').read_text())['versions'] if v['version'] == version)
if backend == 'atomvm':
    for file in Path('/src/atomvm/wasm/src').glob('AtomVM.*'):
        if file.suffix in {'.mjs', '.js', '.wasm'}:
            shutil.copyfile(file, out / file.name)
    for name in ['program.avm', 'atomvmlib.avm', 'source.exs', 'native-smoke.txt', 'ELIXIR-LICENSE']:
        shutil.copyfile(Path('/program') / name, out / name)
    shutil.copyfile('/src/atomvm/LICENSE', out / 'ATOMVM-LICENSE')
    (out / 'THIRD-PARTY-NOTICES.txt').write_text('AtomVM 0.6.6 and its Erlang/Elixir libraries are provided under the included Apache-2.0 license. Sources retain their copyright notices. Built with Emscripten; its generated runtime includes its upstream notices. No Popcorn code is used.\n')
    manifest = {'schemaVersion': 2, 'backend': backend, 'elixir': version, 'compilerOtp': lock['atomvm']['compilerOtp'], 'otp': None, 'target': 'browser-emscripten', 'runtime': 'AtomVM', 'runtimeVersion': lock['atomvm']['version'], 'profile': 'precompiled', 'source': source, 'runtimeSources': lock['atomvm'], 'toolchain': json.loads(Path('/builder/sources.lock.json').read_text())['images']['emsdk'], 'entrypoint': 'AtomVMLab.start/0', 'programSource': 'source.exs', 'capabilities': {'eval': False, 'threads': True, 'wasi': False, 'filesystem': 'ephemeral MEMFS', 'popcorn': False}, 'validation': {'browser': 'not-yet-tested'}}
else:
    raise ValueError('Unsupported backend: ' + backend)
manifest['files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'manifest.json'}
manifest['builderSources'] = {p.relative_to('/builder').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('/builder').rglob('*')) if p.is_file()}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
