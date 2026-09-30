import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

root = Path('/bundle/fs')
out = Path('/artifacts')
manifest = json.loads((out / 'manifest.json').read_text())
manifest.update({'schemaVersion': 2, 'backend': 'popcorn', 'runtimeVersion': '29.0.6', 'framework': {'name': 'Popcorn', 'version': '0.4.0-next.0'}, 'profile': 'popcorn-genserver', 'entrypoint': 'popcorn_lab', 'apps': {}, 'vm': {'boot': 'vm.boot'}})
manifest['capabilities'].update({'popcorn': True, 'genserverBridge': True})
manifest['codePaths'] = ['/lib/' + path.name + '/ebin' for path in sorted((root / 'lib').iterdir())]
(out / 'filesystem.tar.gz').unlink()
shutil.copyfile(root / 'bin/vm.boot', out / 'vm.boot')
for directory in sorted((root / 'lib').iterdir()):
    name = directory.name + '.tar'
    with tarfile.open(out / name, 'w', format=tarfile.USTAR_FORMAT) as archive:
        for file in sorted(directory.rglob('*')):
            if file.is_file():
                data = file.read_bytes()
                entry = tarfile.TarInfo(file.relative_to(root).as_posix())
                entry.size, entry.mode = len(data), 0o644
                archive.addfile(entry, io.BytesIO(data))
    manifest['apps'][directory.name] = {'tar': name}
for file in Path('/sdk').iterdir():
    shutil.copyfile(file, out / file.name)
manifest['files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.is_file() and p.name != 'manifest.json'}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
