"""Package the AtomVM WASI command and its precompiled Elixir program."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

version = sys.argv[1]
out = Path('/artifacts')
out.mkdir(exist_ok=True)
lock = json.loads(Path('/builder/backends.lock.json').read_text())
toolchain = json.loads(Path('/builder/wasi/toolchain.lock.json').read_text())
source = next(v for v in json.loads(Path('/builder/versions.json').read_text())['versions'] if v['version'] == version)
shutil.copyfile('/src/atomvm/wasi/AtomVM.wasm', out / 'AtomVM.wasm')
for name in ['program.avm', 'atomvmlib.avm', 'source.exs', 'native-smoke.txt', 'ELIXIR-LICENSE']:
    shutil.copyfile(Path('/program') / name, out / name)
shutil.copyfile('/src/atomvm/LICENSE', out / 'ATOMVM-LICENSE')
for path in Path('/probes').glob('*.*'):
    shutil.copyfile(path, out / path.name)
(out / 'THIRD-PARTY-NOTICES.txt').write_text('AtomVM 0.6.6 and its libraries retain their upstream Apache-2.0 license and copyright notices. This builder adapts its Unix platform for WASI Preview 1. Built with wasi-sdk 34; no Emscripten or Popcorn code is used.\n')
manifest = {'schemaVersion': 2, 'backend': 'atomvm', 'elixir': version, 'compilerOtp': lock['atomvm']['compilerOtp'], 'otp': None, 'target': 'wasm32-wasip1', 'runtime': 'AtomVM', 'runtimeVersion': lock['atomvm']['version'], 'profile': 'precompiled-wasi-command', 'source': source, 'runtimeSources': lock['atomvm'], 'toolchain': toolchain, 'entrypoint': '_start → AtomVMLab.start/0', 'programSource': 'source.exs', 'capabilities': {'eval': False, 'threads': False, 'wasi': True, 'filesystem': 'WASI preopened directories', 'network': False, 'dynamicNativeCode': False, 'popcorn': False}, 'validation': {'wasi': 'not-yet-tested'}}
manifest['files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file()}
manifest['builderSources'] = {p.relative_to('/builder').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('/builder').rglob('*')) if p.is_file()}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
