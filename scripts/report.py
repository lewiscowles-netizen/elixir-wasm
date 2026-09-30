#!/usr/bin/env python3
"""Record actual build attempts and their first diagnostic, without promoting them to browser passes."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
versions = json.loads((ROOT / 'versions.json').read_text())['versions']
records = []
for version in versions:
    result = ROOT / 'builds/logs' / ('compiler-' + version['version'] + '.json')
    record = {'version': version['version'], 'compilerOtp': '29.0.6', 'status': 'not-attempted', 'browserTested': False}
    if result.exists():
        record.update(json.loads(result.read_text()))
        if record['exitCode']:
            lines = (ROOT / record['log']).read_text(errors='replace').splitlines()
            patterns = ['At least Erlang', 'please re-compile this module', 'syntax error before:', 'cannot escape', 'undefined function', 'Error loading module']
            match = next((line for line in lines if any(pattern in line for pattern in patterns)), None)
            record['diagnostic'] = re.sub(r'^#\d+\s+[0-9.]+\s*', '', match) if match else 'See the compiler log for the first error'
    records.append(record)
report = {'schemaVersion': 1, 'date': '2026-09-29', 'scope': 'Native compilation against OTP 29.0.6; these results are not browser runtime tests', 'sourceLockSha256': hashlib.sha256((ROOT / 'versions.json').read_bytes()).hexdigest(), 'results': records}
(ROOT / 'docs/evidence/compiler-otp29.json').write_text(json.dumps(report, indent=2) + '\n')
rows = ['# Direct compilation on OTP 29', '', 'The catalogue selects the first and latest stable patch of every released minor, starting at 1.0. Source pins, native compilation, browser packaging and browser execution are distinct states.', '', 'This is an OTP 29 compilation experiment, including combinations outside upstream support. Consult the [official compatibility table](https://elixir.hexdocs.pm/compatibility-and-deprecations.html) before interpreting a failure as an Elixir defect. Native compilation success alone does not prove browser support.', '', '| Minor | First stable / compiler result | Latest stable / compiler result |', '| --- | --- | --- |']
by_version = {r['version']: r for r in records}
for series in dict.fromkeys(version['series'] for version in versions):
    releases = [version for version in versions if version['series'] == series]
    first, latest = releases[0], releases[-1]
    rows.append('| ' + first['series'] + ' | ' + first['version'] + ': ' + by_version[first['version']]['status'] + ' | ' + latest['version'] + ': ' + by_version[latest['version']]['status'] + ' |')
rows += ['', 'See the [compiler evidence](../evidence/compiler-otp29.json) for exact diagnostics and log hashes. Browser validation is recorded separately. The historic compiler recipe under `families/historical/` is a separate attempt with an era-appropriate OTP toolchain; it does not change the results of the OTP 29 experiment.']
(ROOT / 'docs/reference/versions.md').write_text('\n'.join(rows) + '\n')
print('Recorded', len([r for r in records if r['status'] != 'not-attempted']), 'compiler attempts')
