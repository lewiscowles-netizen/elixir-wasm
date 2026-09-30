# Browser artifact contract

A direct OTP bundle is exported to `builds/browser-<version>/`. Its files are:

| File | Meaning |
| --- | --- |
| `beam.wasm` | Source-built OTP VM targeting Emscripten |
| `beam.mjs`, `beam.emu.mjs` | Matching Emscripten loader and worker support |
| `filesystem.tar.gz` | Deterministic archive of OTP and selected Elixir bytecode, boot script and lab runner |
| `manifest.json` | Exact source pins, VM version, declared capabilities and file hashes |
| `ELIXIR-LICENSE`, `OTP-LICENSE`, `POPCORN-LICENSE`, `THIRD-PARTY-NOTICES.txt` | Upstream licenses and bundled component notices |

`profile` identifies direct compilation (`core`) or historical retargeting (`historical-retarget`). Retargeted manifests include the original compiler image and declared transformations. Project manifests additionally describe the application and bundled dependencies.

Schema 2 adds a `backend` identity. Earlier manifests imply `direct`. [Popcorn](popcorn.md) exports to `builds/popcorn-<version>/` with its SDK, worker, boot script and application tar files. [AtomVM](atomvm.md) exports to `builds/atomvm-<version>/` with its VM, compiled `.avm` program, runtime library and source. Each backend has a distinct required file contract; relabeling a direct artifact does not satisfy another backend's contract. The lab catalogue uses backend-qualified identities for these additional integrations.

`builderSources` records SHA-256 hashes for the local build scripts, Docker recipes and historical patches included in the build. Upstream pins identify original source; these recipe hashes identify the local adaptation. Locked inputs and normalized filesystem archives do not promise that every toolchain output is reproducible byte for byte across host architectures.

The filesystem archive uses regular USTAR entries, gzip timestamp zero, sorted paths and fixed file metadata. The loader rejects absolute paths, parent traversal and non-file entries. It writes the user's script to `/main.exs` before booting the runtime.

Manifest `validation.browser` begins as `not-yet-tested`. Compilation is not a substitute for a browser test. The lab writes actual execution evidence to `evidence/browser.json`; the builder's documentation can include a generated snapshot under `docs/evidence/`. Evidence identifies exact manifest hashes and the browser used. The original artifact manifest is immutable after testing.

`export-lab.py` checks the complete required file set, every file's size and SHA-256, and the Wasm magic/version bytes. It exports to content-addressed directories and updates `web/runtimes.local.json` after successful verification. A previous exported bundle remains available until deliberately removed.

Keep the JavaScript and Wasm files from the same build. Never combine a VM, boot script or OTP libraries from different versions. Deployment must include the ignored runtime directories and generated local catalogue; a Git checkout by itself contains source, not built runtimes.
