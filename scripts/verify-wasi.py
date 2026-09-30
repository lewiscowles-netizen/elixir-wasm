#!/usr/bin/env python3
"""Execute WASI acceptance probes and bind their evidence to exact artifact hashes."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('exporter', ROOT / 'scripts/export-lab.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundles', nargs='+', type=Path)
    parser.add_argument('--wasmtime', default='wasmtime')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/evidence/wasi.json')
    args = parser.parse_args()
    executable = shutil.which(args.wasmtime)
    if not executable:
        parser.error('Install Wasmtime or supply --wasmtime /path/to/wasmtime')
    host = {'version': subprocess.check_output([executable, '--version'], text=True).strip(), 'executableSha256': hashlib.sha256(Path(executable).read_bytes()).hexdigest()}
    evidence = {'schemaVersion': 1, 'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'host': host, 'verifierSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'results': []}
    for bundle in args.bundles:
        bundle = bundle.resolve()
        manifest = exporter.verify(bundle)
        if manifest['target'] != 'wasm32-wasip1':
            parser.error('Expected a WASI bundle')
        result = {'version': manifest['elixir'], 'backend': manifest['backend'], 'target': manifest['target'], 'manifestSha256': hashlib.sha256((bundle / 'manifest.json').read_bytes()).hexdigest(), 'imports': exporter.wasi_imports((bundle / 'AtomVM.wasm').read_bytes()), 'cases': [], 'status': 'passed'}
        def run(name, mounts, program, expected, flags=()):
            command = [executable, 'run', *flags, *mounts, str(bundle / 'AtomVM.wasm'), '/bundle/' + program, '/bundle/atomvmlib.avm']
            started = time.monotonic()
            try:
                process = subprocess.run(command, capture_output=True, text=True, timeout=30)
                record = {'name': name, 'exitCode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr, 'seconds': round(time.monotonic() - started, 3)}
                expected(record)
                record['status'] = 'passed'
            except (AssertionError, subprocess.TimeoutExpired) as error:
                record = {'name': name, 'status': 'failed', 'error': str(error), **(record if isinstance(error, AssertionError) else {})}
                record['status'] = 'failed'
                result['status'] = 'failed'
            result['cases'].append(record)
            print(manifest['elixir'] + ' ' + name + ': ' + record['status'], flush=True)
        def expect_boot_denied(record):
            assert record['exitCode'] != 0 and 'Failed opening' in record['stderr'], record
        def expect_program(record):
            assert record['exitCode'] == 0, record
        def expect_probe(granted):
            def check(record):
                assert record['exitCode'] == 0, record
                for token in ['COMPILER=' + manifest['elixir'], '{platform,wasi}', '{squares,[1,4,9]}', 'MESSAGE=42', 'FILE=' + ('capability proof' if granted else 'denied')]:
                    assert token in record['stdout'], (token, record)
                elapsed = re.search(r'TIMER_MS=(\d+)', record['stdout'])
                assert elapsed and 20 <= int(elapsed[1]) < 2000, record
                assert record['stdout'].count('ESCAPE=denied') == 2, record
            return check
        def expect_failure(record):
            assert record['exitCode'] != 0 and 'intentional_wasi_failure' in record['stderr'], record
        def expect_fuel(record):
            assert record['exitCode'] != 0 and 'LOOP_STARTED' in record['stdout'] and 'all fuel consumed' in record['stderr'].lower(), record
        with tempfile.TemporaryDirectory(prefix='wasi-permissions-') as temporary:
            root = Path(temporary)
            data = root / 'data'
            data.mkdir()
            (root / 'outside.txt').write_text('must remain inaccessible')
            (data / 'input.txt').write_text('capability proof')
            (data / 'escape.txt').symlink_to('../outside.txt')
            mount = ['--dir', str(bundle) + '::/bundle']
            run('no-preopen-denies-program-loading', [], 'program.avm', expect_boot_denied)
            run('selected-program', mount, 'program.avm', expect_program)
            run('elixir-processes-timer-no-data-grant', mount, 'probe.avm', expect_probe(False))
            run('granted-file-and-denied-escapes', [*mount, '--dir', str(data) + '::/data'], 'probe.avm', expect_probe(True))
            run('elixir-error-is-host-failure', mount, 'failure.avm', expect_failure)
            run('host-fuel-stops-infinite-program', mount, 'loop.avm', expect_fuel, ['-W', 'fuel=100000000'])
        evidence['results'].append(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n')
    if any(result['status'] != 'passed' for result in evidence['results']):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
