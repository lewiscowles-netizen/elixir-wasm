import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const filename = process.argv[2];
if (!filename) throw new Error('Usage: node scripts/inspect-wasm.mjs path/to/beam.wasm');
const bytes = await fs.readFile(filename);
const module = await WebAssembly.compile(bytes);
const imports = WebAssembly.Module.imports(module);
const exports = WebAssembly.Module.exports(module);
console.log(JSON.stringify({ file: filename, sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length, imports, exports, pureWasiPreview1Imports: imports.every(item => item.module === 'wasi_snapshot_preview1'), note: 'Import inspection does not establish host execution compatibility.' }, null, 2));
