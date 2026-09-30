#!/usr/bin/env python3
"""Verify complete runtime bundles and export them to an independent static lab."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def wasi_imports(data):
    offset = 8
    def number():
        nonlocal offset
        value = 0
        for shift in range(0, 35, 7):
            byte = data[offset]
            offset += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                return value
        raise ValueError('Invalid Wasm integer')
    def name():
        nonlocal offset
        length = number()
        result = data[offset:offset + length].decode('utf-8')
        offset += length
        return result
    imports = []
    while offset < len(data):
        section = data[offset]
        offset += 1
        size = number()
        end = offset + size
        if end > len(data):
            raise ValueError('Truncated Wasm section')
        if section == 2:
            for _ in range(number()):
                module, field = name(), name()
                kind = data[offset]
                offset += 1
                if module != 'wasi_snapshot_preview1' or kind != 0:
                    raise ValueError('WASI artifact has a non-WASI function import')
                number()
                imports.append(field)
            if offset != end:
                raise ValueError('Invalid Wasm import section')
        offset = end
    if not imports:
        raise ValueError('Expected WASI Preview 1 imports')
    return imports

def verify(bundle):
    manifest = json.loads((bundle / 'manifest.json').read_text())
    if manifest['target'] not in {'browser-emscripten', 'wasm32-wasip1'}:
        raise ValueError('Unknown artifact target')
    wasi = manifest['target'] == 'wasm32-wasip1'
    backend = manifest.get('backend', 'direct')
    common = {'ELIXIR-LICENSE', 'THIRD-PARTY-NOTICES.txt'}
    profiles = {
        'direct': {'beam.wasm', 'beam.mjs', 'beam.emu.mjs', 'filesystem.tar.gz', 'OTP-LICENSE', 'POPCORN-LICENSE'},
        'popcorn': {'beam.wasm', 'beam.mjs', 'beam.emu.mjs', 'popcorn.mjs', 'popcorn-worker.mjs', 'vm.boot', 'OTP-LICENSE', 'POPCORN-LICENSE'},
        'atomvm': {'AtomVM.wasm', 'AtomVM.mjs', 'program.avm', 'atomvmlib.avm', 'source.exs', 'ATOMVM-LICENSE'},
    }
    if backend not in profiles:
        raise ValueError('Unknown runtime backend')
    required = common | profiles[backend]
    if wasi:
        if backend != 'atomvm' or manifest.get('profile') != 'precompiled-wasi-command':
            raise ValueError('Unsupported WASI backend/profile')
        required = common | (profiles['atomvm'] - {'AtomVM.mjs'}) | {'WASI-LIBC-LICENSE', 'WASI-SDK-LICENSE', 'LLVM-LICENSE', 'TOOLCHAIN-LICENSE-SOURCES.json'}
    if backend == 'popcorn':
        apps = manifest.get('apps', {})
        if not {'kernel', 'stdlib', 'compiler', 'elixir', 'popcorn', 'popcorn_lab'} <= apps.keys():
            raise ValueError('Incomplete Popcorn applications')
        required |= {app['tar'] for app in apps.values()}
    if not required <= manifest['files'].keys():
        raise ValueError('Incomplete runtime manifest')
    for name, record in manifest['files'].items():
        if Path(name).name != name:
            raise ValueError('Invalid artifact path')
        data = (bundle / name).read_bytes()
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            raise ValueError('Artifact checksum mismatch: ' + str(bundle / name))
    wasm = 'AtomVM.wasm' if backend == 'atomvm' else 'beam.wasm'
    if (bundle / wasm).read_bytes()[:8] != b'\x00asm\x01\x00\x00\x00':
        raise ValueError('Invalid WebAssembly header')
    if wasi:
        wasi_imports((bundle / wasm).read_bytes())
    return manifest

def wasi_archive(web, bundle, manifest, identity):
    directory = web / 'downloads'
    directory.mkdir(exist_ok=True)
    archive = directory / (identity + '.tar.gz')
    temporary = archive.with_suffix('.tmp')
    with temporary.open('wb') as stream, gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0) as compressed, tarfile.open(fileobj=compressed, mode='w|', format=tarfile.USTAR_FORMAT) as tar:
        for name in sorted([*manifest['files'], 'manifest.json']):
            data = (bundle / name).read_bytes()
            entry = tarfile.TarInfo(identity + '/' + name)
            entry.size, entry.mode = len(data), 0o644
            tar.addfile(entry, io.BytesIO(data))
    temporary.replace(archive)
    return {'url': archive.relative_to(web).as_posix(), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'bytes': archive.stat().st_size}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lab', type=Path)
    parser.add_argument('bundles', nargs='+', type=Path)
    args = parser.parse_args()
    web = args.lab.resolve() / 'web'
    if not (web / 'index.html').is_file():
        parser.error('Expected an Elixir lab with web/index.html')
    checked = [(bundle, verify(bundle)) for bundle in args.bundles]
    catalogue = web / 'runtimes.local.json'
    runtimes = {r.get('id', r['version']): r for r in json.loads(catalogue.read_text())['runtimes']} if catalogue.exists() else {}
    target = web / 'runtimes'
    target.mkdir(exist_ok=True)
    for bundle, manifest in checked:
        version = manifest['elixir']
        if version not in {v['version'] for v in json.loads((ROOT / 'versions.json').read_text())['versions']}:
            raise ValueError('Version not in source lock: ' + version)
        digest = hashlib.sha256((bundle / 'manifest.json').read_bytes()).hexdigest()[:16]
        app = manifest.get('application', {}).get('name')
        backend = manifest.get('backend', 'direct')
        identity = (backend + '-' if backend != 'direct' else '') + version + ('-' + app if app else '')
        if manifest['target'] == 'wasm32-wasip1':
            identity = 'wasi-' + identity
        if any(character not in 'abcdefghijklmnopqrstuvwxyz0123456789.-_' for character in identity):
            raise ValueError('Invalid bundle identity')
        name = identity + '-' + digest
        destination = target / name
        if destination.exists():
            verify(destination)
            if (destination / 'manifest.json').read_bytes() != (bundle / 'manifest.json').read_bytes():
                raise ValueError('Existing export has a different manifest: ' + str(destination))
        else:
            with tempfile.TemporaryDirectory(dir=target) as temporary:
                staged = Path(temporary) / name
                shutil.copytree(bundle, staged)
                staged.rename(destination)
        runtimes[identity] = {'id': identity, 'backend': backend, 'application': app, 'version': version, 'otp': manifest['otp'], 'runtimeVersion': manifest.get('runtimeVersion', manifest['otp']), 'framework': manifest.get('framework'), 'eval': manifest.get('capabilities', {}).get('eval', True), 'programSource': manifest.get('programSource'), 'profile': manifest['profile'], 'compilerOtp': manifest.get('retargeting', {}).get('originalCompilerOtp', manifest.get('compilerOtp', manifest['otp'])), 'directory': 'runtimes/' + name + '/', 'status': 'built', 'manifestSha256': hashlib.sha256((bundle / 'manifest.json').read_bytes()).hexdigest()}
        runtimes[identity]['target'] = manifest['target']
        if manifest['target'] == 'wasm32-wasip1':
            runtimes[identity]['archive'] = wasi_archive(web, bundle, manifest, identity)
    temporary = catalogue.with_suffix('.tmp')
    temporary.write_text(json.dumps({'schemaVersion': 1, 'runtimes': list(runtimes.values())}, indent=2) + '\n')
    temporary.replace(catalogue)
    shutil.copyfile(ROOT / 'versions.json', web / 'versions.json')
    shutil.copytree(ROOT / 'docs', args.lab.resolve() / 'docs', dirs_exist_ok=True)
    (args.lab.resolve() / 'docs/SOURCE.json').write_text(json.dumps({'source': 'elixir-wasm-builder/docs', 'files': {str(path.relative_to(ROOT / 'docs')): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((ROOT / 'docs').rglob('*')) if path.is_file()}}, indent=2) + '\n')
    print('Exported ' + str(len(checked)) + ' verified artifact bundles')

if __name__ == '__main__':
    main()
