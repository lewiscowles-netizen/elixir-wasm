import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('exporter', ROOT / 'scripts/export-lab.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

class ContractTests(unittest.TestCase):
    def fixture(self, root):
        files = {'beam.wasm': b'\x00asm\x01\x00\x00\x00', 'beam.mjs': b'loader', 'beam.emu.mjs': b'worker', 'filesystem.tar.gz': b'fs', 'ELIXIR-LICENSE': b'elixir', 'OTP-LICENSE': b'otp', 'POPCORN-LICENSE': b'popcorn', 'THIRD-PARTY-NOTICES.txt': b'notices'}
        for name, data in files.items():
            (root / name).write_bytes(data)
        manifest = {'target': 'browser-emscripten', 'files': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} for name, data in files.items()}}
        (root / 'manifest.json').write_text(json.dumps(manifest))
        return manifest

    def test_export_rejects_tampered_bundle_before_copying(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            exporter.verify(root)
            (root / 'beam.mjs').write_bytes(b'edited')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                exporter.verify(root)

    def test_manifest_cannot_escape_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.fixture(root)
            manifest['files']['../outside'] = {'bytes': 0, 'sha256': ''}
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Invalid artifact path'):
                exporter.verify(root)

    def test_a_direct_bundle_cannot_be_relabelled_as_atomvm(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.fixture(root)
            manifest['backend'] = 'atomvm'
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Incomplete runtime manifest'):
                exporter.verify(root)

    def test_popcorn_requires_its_application_and_sdk_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.fixture(root)
            manifest['backend'] = 'popcorn'
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Incomplete Popcorn applications'):
                exporter.verify(root)

    def test_backend_compatibility_and_target_fail_before_docker(self):
        for arguments in [['1.0.0', '--backend', 'atomvm'], ['1.17.3', '--backend', 'popcorn'], ['1.20.4', '--backend', 'atomvm', '--target', 'wasi'], ['1.20.4', '--backend', 'popcorn', '--target', 'wasi']]:
            with self.subTest(arguments=arguments):
                result = subprocess.run(['python3', str(ROOT / 'scripts/build.py'), *arguments, '--print'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')

    def test_wasi_uses_a_separate_recipe_and_native_compiler_dependency(self):
        result = subprocess.run(['python3', str(ROOT / 'scripts/build.py'), '1.17', '--backend', 'atomvm', '--target', 'wasi', '--print'], capture_output=True, text=True, check=True)
        plan = json.loads(result.stdout)
        self.assertEqual(len(plan['group']['default']['targets']), 2)
        for name in plan['group']['default']['targets']:
            target = plan['target'][name]
            self.assertEqual(target['dockerfile'], 'families/wasi/Dockerfile')
            self.assertIn('/wasi-atomvm-', target['output'][0])
            compiler = plan['target'][target['contexts']['compiler-base'][7:]]
            self.assertEqual(compiler['target'], 'compiler')
            self.assertEqual(len(target['args']['SDK_SHA256']), 64)

    def test_wasi_import_contract_rejects_javascript_host_dependencies(self):
        def module(namespace):
            imports = bytes([1, len(namespace)]) + namespace + bytes([9]) + b'proc_exit' + bytes([0, 0])
            return b'\x00asm\x01\x00\x00\x00\x01\x04\x01\x60\x00\x00' + bytes([2, len(imports)]) + imports
        self.assertEqual(exporter.wasi_imports(module(b'wasi_snapshot_preview1')), ['proc_exit'])
        with self.assertRaisesRegex(ValueError, 'non-WASI'):
            exporter.wasi_imports(module(b'env'))

    def test_reimport_rejects_corruption_in_an_existing_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle, lab = root / 'bundle', root / 'lab'
            bundle.mkdir()
            (lab / 'web').mkdir(parents=True)
            (lab / 'web/index.html').write_text('<!doctype html>')
            manifest = self.fixture(bundle)
            manifest.update({'elixir': '1.20.4', 'otp': '29.0.6', 'profile': 'core'})
            (bundle / 'manifest.json').write_text(json.dumps(manifest))
            command = ['python3', str(ROOT / 'scripts/export-lab.py'), str(lab), str(bundle)]
            subprocess.run(command, capture_output=True, text=True, check=True)
            runtime = next((lab / 'web/runtimes').iterdir())
            (runtime / 'beam.mjs').write_text('corrupted export')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Artifact checksum mismatch', result.stderr)

    def test_wasi_request_never_invokes_browser_recipe(self):
        result = subprocess.run(['python3', str(ROOT / 'scripts/build.py'), '1.20.4', '--target', 'wasi', '--print'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('No WASI runtime port', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_minor_selection_resolves_both_stable_endpoints(self):
        result = subprocess.run(['python3', str(ROOT / 'scripts/build.py'), '1.0', '--print'], capture_output=True, text=True, check=True)
        bake = json.loads(result.stdout)
        self.assertEqual({t['args']['ELIXIR_VERSION'] for t in bake['target'].values()}, {'1.0.0', '1.0.5'})
        for name in bake['group']['default']['targets']:
            browser = bake['target'][name]
            native = bake['target'][browser['contexts']['historical-input'][7:]]
            self.assertEqual(browser['target'], 'historical-browser-artifacts')
            self.assertTrue(native['args']['COMPILER_IMAGE'].startswith('erlang:17.5@sha256:'))
            self.assertEqual(len(native['args']['ELIXIR_SHA256']), 64)

    def test_refresh_does_not_bless_a_modified_locked_archive(self):
        spec = importlib.util.spec_from_file_location('locker', ROOT / 'scripts/lock-sources.py')
        locker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(locker)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'sources').mkdir()
            (root / 'sources/elixir.tar.gz').write_bytes(b'changed')
            entry = {'file': 'elixir.tar.gz', 'url': 'https://example.invalid/source'}
            previous = {**entry, 'sha256': hashlib.sha256(b'original').hexdigest()}
            with patch.object(locker, 'ROOT', root), self.assertRaisesRegex(ValueError, 'differs from its existing lock'):
                locker.download(entry, previous)

if __name__ == '__main__':
    unittest.main()
