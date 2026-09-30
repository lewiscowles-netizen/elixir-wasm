#!/usr/bin/env python3
"""Build exact Elixir versions through Buildx; keep source availability separate from validation."""
import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('versions', nargs='*', help='Exact versions or minor series; a series selects first and latest stable')
    parser.add_argument('--project', type=Path, help='Compiled Mix application build context; use with one exact version')
    parser.add_argument('--app', help='OTP application name for the project')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--target', choices=['browser', 'compiler', 'wasi'], default='browser')
    parser.add_argument('--backend', choices=['direct', 'popcorn', 'atomvm'], default='direct')
    parser.add_argument('--script', type=Path, help='AtomVM script to compile before browser execution')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--parallel', type=int, default=1)
    parser.add_argument('--print', action='store_true', dest='print_only')
    parser.add_argument('--offline', action='store_true', help='Require source archives already cached; Docker toolchain layers must also be available')
    args = parser.parse_args()
    if args.jobs < 1 or args.parallel < 1:
        parser.error('jobs and parallel must be positive')
    if args.backend != 'direct':
        from build_backends import build
        return build(args, parser)
    if args.script:
        parser.error('--script requires --backend atomvm; direct evaluates source in the browser')
    if args.target == 'wasi':
        parser.error('No WASI runtime port is implemented for direct OTP. Use --backend atomvm with a configured release for the separate WASI command. See docs/reference/wasi.md.')
    versions = json.loads((ROOT / 'versions.json').read_text())['versions']
    known = {v['version'] for v in versions} | {v['series'] for v in versions}
    if set(args.versions) - known:
        parser.error('Unknown selection: ' + ', '.join(sorted(set(args.versions) - known)))
    if not args.all and not args.versions:
        parser.error('Select versions, minor series or --all')
    selected = [v for v in versions if args.all or v['version'] in args.versions or v['series'] in args.versions]
    if args.project and (len(selected) != 1 or not args.app or args.target != 'browser'):
        parser.error('--project needs one exact version, --app, and --target browser')
    if args.app and (not args.project or not re.fullmatch(r'[a-z][a-z0-9_]*', args.app)):
        parser.error('--app must be a lowercase OTP application name and needs --project')
    if args.project and selected[0]['series'] != '1.20':
        parser.error('Project bundling currently supports the 1.20 compiler family; historical retargeting supports scripts only')
    stage = 'browser-artifacts' if args.target == 'browser' else 'elixir-artifacts'
    lock = json.loads((ROOT / 'sources.lock.json').read_text())
    families = json.loads((ROOT / 'families/historical/compilers.json').read_text())['families']
    targets = {}
    dependencies = {}
    for entry in selected:
        v = entry['version']
        targets['elixir-' + v.replace('.', '-')] = {'context': str(ROOT), 'dockerfile': 'Dockerfile', 'target': stage, 'args': {'ELIXIR_VERSION': v, 'JOBS': str(args.jobs), 'EMSDK_IMAGE': lock['images']['emsdk'], 'OTP_IMAGE': lock['images']['otp']}, 'output': ['type=local,dest=' + str(ROOT / 'builds' / (args.target + '-' + v))]}
        if args.target == 'browser' and entry['series'].startswith('1.') and int(entry['series'].split('.')[1]) < 20:
            family = next(f for f in families if f['minMinor'] <= int(entry['series'].split('.')[1]) <= f['maxMinor'])
            native_name = 'native-' + v.replace('.', '-')
            dependencies[native_name] = {'context': str(ROOT), 'dockerfile': 'families/historical/Dockerfile', 'args': {'ELIXIR_VERSION': v, 'ELIXIR_SHA256': entry['sha256'], 'COMPILER_IMAGE': family['image']}}
            target = targets['elixir-' + v.replace('.', '-')]
            target['target'] = 'historical-browser-artifacts'
            target['contexts'] = {'historical-input': 'target:' + native_name}
            target['args'].update({'HISTORICAL_OTP': family['otp'], 'HISTORICAL_IMAGE': family['image']})
    if args.project:
        for target in targets.values():
            target['target'] = 'project-artifacts'
            target['contexts'] = {'project-source': str(args.project.resolve())}
            target['args']['APP_NAME'] = args.app
            target['output'] = ['type=local,dest=' + str(ROOT / 'builds' / ('project-' + args.app + '-' + selected[0]['version']))]
    bake = {'group': {'default': {'targets': list(targets)}}, 'target': {**dependencies, **targets}}
    if args.print_only:
        print(json.dumps(bake, indent=2))
        return
    spec = importlib.util.spec_from_file_location('fetch_sources', ROOT / 'scripts/fetch.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.fetch(lock['sources'] + selected + [v for v in versions if v['version'] == '1.20.4'], args.offline)
    logs = ROOT / 'builds/logs'
    logs.mkdir(parents=True, exist_ok=True)
    def build(item):
        name, target = item
        version = target['args']['ELIXIR_VERSION']
        run_id = ('project-' + args.app if args.project else args.target) + '-' + version
        logfile = logs / (run_id + '.log')
        context = target.get('contexts', {}).get('historical-input', '')
        required = {context[7:]: dependencies[context[7:]]} if context.startswith('target:') else {}
        config = {'group': {'default': {'targets': [name]}}, 'target': {**required, name: target}}
        command = ['docker', 'buildx', 'bake', '--allow', 'fs.write=' + str(ROOT / 'builds'), '-f', '-', '--progress', 'plain']
        if args.project:
            command += ['--allow', 'fs.read=' + str(args.project.resolve())]
        preparation = {'browser-artifacts': 'packaged', 'historical-browser-artifacts': 'historical-packaged', 'project-artifacts': 'project-packaged'}.get(target['target'])
        phases = ([{**target, 'target': preparation, 'output': ['type=cacheonly']}] if preparation else []) + [target]
        outcomes = []
        with logfile.open('w') as output:
            for phase in phases:
                config['target'][name] = phase
                output.write('Buildx phase: ' + phase['target'] + '\n')
                output.flush()
                started = time.monotonic()
                result = subprocess.run(command, input=json.dumps(config), text=True, stdout=output, stderr=subprocess.STDOUT, cwd=ROOT)
                outcomes.append({'target': phase['target'], 'exitCode': result.returncode, 'seconds': round(time.monotonic() - started, 3)})
                if result.returncode:
                    break
        record = {'version': version, 'target': args.target, 'application': args.app, 'status': 'built' if result.returncode == 0 else 'build-failed', 'exitCode': result.returncode, 'phases': outcomes, 'log': str(logfile.relative_to(ROOT)), 'logSha256': hashlib.sha256(logfile.read_bytes()).hexdigest(), 'time': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'browserTested': False}
        print(version + ': ' + record['status'] + ' (' + record['log'] + ')', flush=True)
        (logs / (run_id + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        results = list(pool.map(build, targets.items()))
    (ROOT / 'builds' / (('project-' + args.app if args.project else args.target) + '-results.json')).write_text(json.dumps(results, indent=2) + '\n')
    if any(r['exitCode'] for r in results):
        sys.exit(1)

if __name__ == '__main__':
    main()
