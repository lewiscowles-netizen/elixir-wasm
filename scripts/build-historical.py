#!/usr/bin/env python3
"""Build with an era-appropriate OTP compiler, then try the explicit browser retargeting experiment."""
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('versions', nargs='*')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--parallel', type=int, default=2)
    parser.add_argument('--print', action='store_true', dest='print_only')
    args = parser.parse_args()
    versions = json.loads((ROOT / 'versions.json').read_text())['versions']
    known = {v['version'] for v in versions} | {v['series'] for v in versions}
    if set(args.versions) - known or args.parallel < 1 or (not args.versions and not args.all):
        parser.error('Choose known exact versions or minor series, or --all; parallel must be positive')
    families = json.loads((ROOT / 'families/historical/compilers.json').read_text())['families']
    selected = [v for v in versions if v['series'].startswith('1.') and int(v['series'].split('.')[1]) < 20 and (args.all or v['version'] in args.versions or v['series'] in args.versions)]
    if not selected:
        parser.error('Use scripts/build.py for Elixir 1.20')
    plans = []
    for entry in selected:
        minor = int(entry['series'].split('.')[1])
        family = next(f for f in families if f['minMinor'] <= minor <= f['maxMinor'])
        output = ROOT / 'builds' / ('historical-' + entry['version'])
        native = ['docker', 'buildx', 'build', '-f', 'families/historical/Dockerfile', '--build-arg', 'COMPILER_IMAGE=' + family['image'], '--build-arg', 'ELIXIR_VERSION=' + entry['version'], '--build-arg', 'ELIXIR_SHA256=' + entry['sha256'], '--output', 'type=local,dest=' + str(output), '--progress', 'plain', '.']
        browser = ['docker', 'buildx', 'build', '--target', 'historical-browser-artifacts', '--build-arg', 'ELIXIR_VERSION=' + entry['version'], '--build-arg', 'HISTORICAL_OTP=' + family['otp'], '--build-arg', 'HISTORICAL_IMAGE=' + family['image'], '--build-context', 'historical-input=' + str(output), '--output', 'type=local,dest=' + str(ROOT / 'builds' / ('historical-browser-' + entry['version'])), '--progress', 'plain', '.']
        plans.append({'version': entry['version'], 'compiler': family, 'native': native, 'browser': browser})
    if args.print_only:
        print(json.dumps(plans, indent=2))
        return
    spec = importlib.util.spec_from_file_location('fetch_sources', ROOT / 'scripts/fetch.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.fetch(json.loads((ROOT / 'sources.lock.json').read_text())['sources'] + selected + [v for v in versions if v['version'] == '1.20.4'])
    logs = ROOT / 'builds/logs'
    logs.mkdir(parents=True, exist_ok=True)
    def build(plan):
        record = {'version': plan['version'], 'compiler': plan['compiler'], 'profile': 'historical-retarget', 'browserTested': False}
        for stage in ['native'] + ([] if args.native_only else ['browser']):
            logfile = logs / ('historical-' + stage + '-' + plan['version'] + '.log')
            with logfile.open('w') as output:
                result = subprocess.run(plan[stage], cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
            record[stage] = {'exitCode': result.returncode, 'log': str(logfile.relative_to(ROOT)), 'logSha256': hashlib.sha256(logfile.read_bytes()).hexdigest()}
            print(plan['version'] + ' ' + stage + ': ' + ('built' if result.returncode == 0 else 'failed'), flush=True)
            if result.returncode:
                break
        (logs / ('historical-' + plan['version'] + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        return record
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        results = list(pool.map(build, plans))
    (ROOT / 'builds/historical-results.json').write_text(json.dumps(results, indent=2) + '\n')
    if any(r.get('native', {}).get('exitCode') or r.get('browser', {}).get('exitCode') for r in results):
        sys.exit(1)

if __name__ == '__main__':
    main()
