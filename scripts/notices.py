"""Collect upstream licensing material into a redistributable notice file."""
from pathlib import Path
import tarfile


def collect(out):
    parts = ['Elixir WebAssembly experimental build\nSources and local modifications are identified in manifest.json.\n']
    for archive in [Path('/selected-source.tar.gz'), Path('/sources/otp.tar.gz'), Path('/sources/popcorn.tar.gz')]:
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                name = Path(member.name).name.lower()
                if member.isfile() and (name in {'license', 'license.txt', 'license.md', 'copying', 'notice', 'legal'} or '/LICENSES/' in member.name):
                    content = source.extractfile(member).read().decode('utf-8', errors='replace')
                    parts.append('\n--- ' + member.name + ' ---\n' + content)
    for filename in ['/emsdk/upstream/emscripten/LICENSE', '/emsdk/upstream/emscripten/system/lib/libc/musl/COPYRIGHT']:
        path = Path(filename)
        if path.is_file():
            parts.append('\n--- ' + filename + ' ---\n' + path.read_text(errors='replace'))
    (out / 'THIRD-PARTY-NOTICES.txt').write_text('\n'.join(parts))
