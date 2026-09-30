#!/usr/bin/env python3
"""Join measured native, packaging and browser results without conflating their guarantees."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lab', type=Path, default=ROOT.parent / 'elixir-wasm-lab')
args = parser.parse_args()
evidence_file = args.lab / 'evidence/browser.json'
evidence = json.loads(evidence_file.read_text()) if evidence_file.exists() else {'results': []}
records = []
for source in json.loads((ROOT / 'versions.json').read_text())['versions']:
    version = source['version']
    record = {'version': version, 'sourceSha256': source['sha256'], 'native': 'not-attempted', 'bundle': 'not-attempted', 'browser': 'not-tested'}
    native = ROOT / 'builds/logs' / (('compiler-' if source['series'] == '1.20' else 'historical-') + version + '.json')
    if native.exists():
        result = json.loads(native.read_text())
        record['nativeEvidence'] = result
        record['native'] = 'passed' if result.get('native', result).get('exitCode') == 0 else 'failed'
    result_file = ROOT / 'builds/logs' / ('browser-' + version + '.json')
    if result_file.exists():
        result = json.loads(result_file.read_text())
        record['bundleEvidence'] = result
        record['bundle'] = 'built' if result['exitCode'] == 0 else 'failed'
        if record['bundle'] == 'built':
            record['native'] = 'passed'
            record['nativeDependencyEvidence'] = 'The successful Buildx browser target requires its selected native compiler stage to succeed.'
    manifest_file = ROOT / 'builds' / ('browser-' + version) / 'manifest.json'
    if record['bundle'] == 'built' and manifest_file.exists():
        digest = hashlib.sha256(manifest_file.read_bytes()).hexdigest()
        record['manifestSha256'] = digest
        for test in evidence['results']:
            proof = test.get('evidence')
            if proof and proof['manifestSha256'] == digest:
                record['browser'] = test['status']
                record['browserEvidence'] = test
    records.append(record)
report = {'schemaVersion': 1, 'scope': 'Core version/arithmetic/modules/processes/files probes; not complete standard-library or historical-OTP compatibility', 'browserEvidenceTime': evidence.get('time'), 'labSourceHashes': evidence.get('labSourceHashes'), 'results': records}
(ROOT / 'docs/evidence/validation.json').write_text(json.dumps(report, indent=2) + '\n')
if evidence_file.exists():
    (ROOT / 'docs/evidence/browser.json').write_bytes(evidence_file.read_bytes())
rows = ['# Measured compatibility', '', 'Each column records a different operation. Historical entries execute retargeted Elixir on OTP 29, subject to the [family limitations](historical-families.md). A browser pass covers the [acceptance probes](../how-to/test.md), not every API. A successful browser build also establishes that its required native compiler stage passed; earlier standalone failures remain in the evidence.', '', '| Elixir | Native compiler stage | Browser bundle | Chromium execution |', '| --- | --- | --- | --- |']
rows += ['| ' + ' | '.join(record[key] for key in ['version', 'native', 'bundle', 'browser']) + ' |' for record in records]
rows += ['', 'The [machine-readable evidence](../evidence/validation.json) includes source and manifest hashes. The [separate OTP 29 compiler experiment](../evidence/compiler-otp29.json) deliberately includes unsupported native combinations; it is not the historical family recipe. WASI results are recorded separately in the [WASI reference](wasi.md).']
(ROOT / 'docs/reference/validation.md').write_text('\n'.join(rows) + '\n')
print('Browser passes:', sum(record['browser'] == 'passed' for record in records), '/', len(records))
