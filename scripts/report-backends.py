#!/usr/bin/env python3
"""Report runtime integration results only when exact manifest hashes match browser evidence."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lab', type=Path, default=ROOT.parent / 'elixir-wasm-lab')
args = parser.parse_args()
catalogue = json.loads((args.lab / 'web/runtimes.local.json').read_text())['runtimes']
evidence = json.loads((args.lab / 'evidence/browser.json').read_text())
records = []
for runtime in catalogue:
    if runtime.get('target', 'browser-emscripten') != 'browser-emscripten':
        continue
    proof = next((test for test in evidence['results'] if test.get('evidence') and test['evidence']['manifestSha256'] == runtime['manifestSha256']), None)
    records.append({'id': runtime['id'], 'backend': runtime.get('backend', 'direct'), 'elixir': runtime['version'], 'manifestSha256': runtime['manifestSha256'], 'browser': proof['status'] if proof else 'not-tested', 'application': runtime.get('application')})
report = {'schemaVersion': 1, 'time': evidence['time'], 'scope': 'Backend-specific example execution, not full library compatibility', 'results': records}
(ROOT / 'docs/evidence/backends.json').write_text(json.dumps(report, indent=2) + '\n')
rows = ['# Runtime integrations', '', 'The backend selects a runtime and application interface. The execution target selects a host contract; all three integrations have browser recipes. AtomVM also has a separate [WASI command target](wasi.md), with [host execution evidence](../evidence/wasi.json). The counts below cover browser execution only.', '', '| Backend | Application interface | Elixir selection means | Measured browser bundles |', '| --- | --- | --- | --- |']
descriptions = {'direct': ('[Direct OTP](../explanation/direct-otp.md)', 'Small script runner; attributed Popcorn VM patches', 'Compiler and bundled Elixir libraries'), 'popcorn': ('[Popcorn](popcorn.md)', 'Upstream JavaScript SDK and Elixir GenServer bridge', 'Compiler and bundled Elixir libraries'), 'atomvm': ('[AtomVM](atomvm.md)', 'Stock runtime; precompiled program', 'Native compiler; AtomVM supplies its own library subset')}
for backend, description in descriptions.items():
    selected = [r for r in records if r['backend'] == backend]
    rows.append('| ' + ' | '.join([*description, str(sum(r['browser'] == 'passed' for r in selected)) + '/' + str(len(selected)) + ' passed']) + ' |')
rows += ['', 'Counts include application variants. The [direct release matrix](validation.md) separately lists its 42 locked release endpoints. Historical retargeting is specific to that route. Compatibility is not inherited by a new backend merely because its version dropdown contains the same source catalogue.', '', '| Integration bundle | Chromium result |', '| --- | --- |']
rows += ['| ' + r['id'] + ' | ' + r['browser'] + ' |' for r in sorted(records, key=lambda r: r['id']) if r['backend'] != 'direct']
rows += ['', 'The [machine-readable evidence](../evidence/backends.json) records exact manifest hashes. Browser tests also cover a JavaScript round trip and lifecycle/error handling for Popcorn, and read-only source plus the compiled example for AtomVM. An unavailable release stays disabled in the UI. The CLI rejects unconfigured compiler families before Docker runs.', '', 'Choose an integration with `--backend direct`, `--backend popcorn` or `--backend atomvm`. Each exports to a distinct catalogue identity, so importing one cannot replace another backend at the same Elixir version. See the [Popcorn build guide](../how-to/popcorn.md) and [AtomVM build guide](../how-to/atomvm.md).']
(ROOT / 'docs/reference/backends.md').write_text('\n'.join(rows) + '\n')
print('Backend browser passes:', sum(r['browser'] == 'passed' for r in records), '/', len(records))
