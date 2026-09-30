"""Build runtime integrations with their own compatibility and packaging contracts."""
import concurrent.futures
import datetime
import hashlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]

def build(args, parser):
    if args.target != 'browser' and not (args.backend == 'atomvm' and args.target == 'wasi'):
        parser.error('The selected backend does not provide this target; WASI is available with --backend atomvm')
    lock = json.loads((ROOT / 'families/backends.lock.json').read_text())
    toolchain = json.loads((ROOT / 'sources.lock.json').read_text())
    wasi = args.target == 'wasi'
    if wasi:
        wasi_lock = json.loads((ROOT / 'families/wasi/toolchain.lock.json').read_text())
        if platform.machine().lower() not in {'arm64', 'aarch64', 'x86_64', 'amd64'}:
            parser.error('The WASI SDK build host must be arm64 or x86_64')
        architecture = 'arm64' if platform.machine() in {'arm64', 'aarch64'} else 'x86_64'
        sdk = wasi_lock['sdk']['wasi-sdk-34.0-' + architecture + '-linux.tar.gz']
    versions = json.loads((ROOT / 'versions.json').read_text())['versions']
    selected = [v for v in versions if args.all or v['version'] in args.versions or v['series'] in args.versions]
    if not selected or set(args.versions) - {value for v in versions for value in [v['version'], v['series']]}:
        parser.error('Select known exact versions, minor series or --all')
    unsupported = [v['version'] for v in selected if v['series'] not in lock[args.backend]['elixirSeries']]
    if unsupported:
        parser.error(args.backend + ' has no configured compiler route for: ' + ', '.join(unsupported))
    if args.project or args.app:
        parser.error('These backend recipes use their documented examples; use direct for --project bundling')
    if args.backend == 'popcorn' and args.script:
        parser.error('Popcorn evaluates source in the browser; --script is for AtomVM precompilation')
    script = (args.script or ROOT / ('examples/wasi/hello.exs' if wasi else 'examples/atomvm/hello.exs')).resolve()
    if args.backend == 'atomvm' and not script.is_file():
        parser.error('The AtomVM script does not exist: ' + str(script))
    from fetch import fetch
    if not args.print_only:
        inputs = [lock['atomvm']] if args.backend == 'atomvm' else toolchain['sources'] + [v for v in versions if v['version'] == '1.20.4']
        fetch(inputs + selected + ([sdk] if wasi else []), args.offline)
    with tempfile.TemporaryDirectory(prefix='elixir-backend-') as temporary:
        context = Path(temporary)
        if args.print_only and args.backend == 'atomvm':
            context = ROOT / 'builds/inputs' / hashlib.sha256(script.read_bytes()).hexdigest()
            context.mkdir(parents=True, exist_ok=True)
        if args.backend == 'atomvm':
            shutil.copyfile(script, context / 'source.exs')
        targets = {}
        dependencies = {}
        for entry in selected:
            version = entry['version']
            identity = ('wasi-' if wasi else '') + args.backend + '-' + version
            name = identity.replace('.', '-')
            target = {'context': str(ROOT), 'dockerfile': 'families/' + args.backend + '/Dockerfile', 'target': 'artifacts', 'args': {'ELIXIR_VERSION': version, 'ELIXIR_SHA256': entry['sha256'], 'EMSDK_IMAGE': toolchain['images']['emsdk']}, 'output': ['type=local,dest=' + str(ROOT / 'builds' / (args.backend + '-' + version))]}
            if args.backend == 'atomvm':
                target['args'].update({'ATOMVM_SHA256': lock['atomvm']['sha256'], 'COMPILER_IMAGE': lock['atomvm']['compilerImage']})
                target['contexts'] = {'program-source': str(context)}
            else:
                base_name = name + '-base'
                dependencies[base_name] = {'context': str(ROOT), 'dockerfile': 'Dockerfile', 'target': 'packaged', 'args': {'ELIXIR_VERSION': version, 'JOBS': str(args.jobs), 'EMSDK_IMAGE': toolchain['images']['emsdk'], 'OTP_IMAGE': toolchain['images']['otp']}}
                target['contexts'] = {'otp-base': 'target:' + base_name}
                target['args'].update({'JS_IMAGE': lock['popcorn']['jsBuilderImage'], 'POPCORN_SHA256': lock['popcorn']['source']['sha256']})
            targets[name] = target
            if wasi:
                base_name = name + '-base'
                dependencies[base_name] = {**target, 'target': 'compiler', 'output': ['type=cacheonly']}
                targets[name] = {'context': str(ROOT), 'dockerfile': 'families/wasi/Dockerfile', 'target': 'artifacts', 'platforms': ['linux/' + ('arm64' if architecture == 'arm64' else 'amd64')], 'contexts': {'compiler-base': 'target:' + base_name}, 'args': {'ELIXIR_VERSION': version, 'BUILD_IMAGE': lock['popcorn']['jsBuilderImage'], 'ATOMVM_SHA256': lock['atomvm']['sha256'], 'SDK_FILE': sdk['file'], 'SDK_SHA256': sdk['sha256']}, 'output': ['type=local,dest=' + str(ROOT / 'builds' / identity)]}
        plan = {'group': {'default': {'targets': list(targets)}}, 'target': {**dependencies, **targets}}
        if args.print_only:
            print(json.dumps(plan, indent=2))
            return
        logs = ROOT / 'builds/logs'
        logs.mkdir(parents=True, exist_ok=True)
        def execute(item):
            name, target = item
            identity = ('wasi-' if wasi else '') + args.backend + '-' + target['args']['ELIXIR_VERSION']
            log = logs / (identity + '.log')
            phases = []
            with log.open('w') as output:
                for stage, outputs in [('packaged', ['type=cacheonly']), ('artifacts', target['output'])]:
                    phase = {**target, 'target': stage, 'output': outputs}
                    required = {name + '-base': dependencies[name + '-base']} if name + '-base' in dependencies else {}
                    config = {'group': {'default': {'targets': [name]}}, 'target': {**required, name: phase}}
                    started = time.monotonic()
                    result = subprocess.run(['docker', 'buildx', 'bake', '--allow', 'fs.read=' + temporary, '--allow', 'fs.write=' + str(ROOT / 'builds'), '-f', '-', '--progress', 'plain'], input=json.dumps(config), text=True, stdout=output, stderr=subprocess.STDOUT, cwd=ROOT)
                    phases.append({'target': stage, 'exitCode': result.returncode, 'seconds': round(time.monotonic() - started, 3)})
                    if result.returncode:
                        break
            record = {'target': args.target, 'backend': args.backend, 'version': target['args']['ELIXIR_VERSION'], 'status': 'built' if result.returncode == 0 else 'build-failed', 'exitCode': result.returncode, 'phases': phases, 'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'logSha256': hashlib.sha256(log.read_bytes()).hexdigest()}
            (logs / (identity + '.json')).write_text(json.dumps(record, indent=2) + '\n')
            print(identity + ': ' + record['status'], flush=True)
            return result.returncode
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
            results = list(pool.map(execute, targets.items()))
        if any(results):
            raise SystemExit(1)
