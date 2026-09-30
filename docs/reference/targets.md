# Target reference

| Property | `browser` | `wasi` |
| --- | --- | --- |
| Implementations | Direct OTP, Popcorn, stock AtomVM | Adapted AtomVM 0.6.6 |
| Toolchain | Emscripten 6.0.2 | wasi-sdk 34, Preview 1 |
| Executable | Wasm plus JavaScript glue and bytecode assets | `AtomVM.wasm` command plus bytecode packs |
| Host | Browser, workers and required cross-origin isolation | WASI Preview 1 host; measured in Wasmtime |
| Files | Temporary Emscripten filesystem | Explicit preopened directories |
| Code evaluation | Direct OTP and Popcorn only | Precompiled Elixir only |
| Scope and limitations | [Runtime integrations](backends.md) | [WASI command reference](wasi.md) |

The lab runs browser bundles locally. Its WASI selection provides downloads, artifact hashes and host commands. Direct OTP and Popcorn reject WASI requests because they have no corresponding recipe.

The development server binds `127.0.0.1`, defaults to port 8130, and emits `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`. Remote deployment needs HTTPS. Browser execution requires `crossOriginIsolated === true`; a WASI command has no dependency on that server or those headers.

`compiler` is a diagnostic build target that exports native-compiled BEAM libraries. Its success alone proves neither browser startup nor WASI execution. See the [direct compiler experiment](versions.md).
