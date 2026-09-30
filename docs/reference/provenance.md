# Source provenance

| Component | Locked identity | Role |
| --- | --- | --- |
| Erlang/OTP | `29.0.6`, commit `e07fd07837e5aa845657f5fa340637121e451d47` | VM and native build tools |
| Popcorn | Commit `bea24dd50fec39a5859e49c54d496736a3c6857a`, reports `0.4.0-next.0` | OTP browser patches and BEAM library patcher |
| Emscripten | `6.0.2`, image digest in `sources.lock.json` | C/C++ to browser Wasm toolchain |
| Autoconf | `2.72` | Regenerate OTP configure scripts |
| Elixir | Each exact release in `versions.json` | Selected compiler and library sources |

Archive URLs and SHA-256 values have one machine-readable home: `sources.lock.json` and `versions.json` at the repository root. They are verified before extraction. Popcorn is pinned to an observed commit rather than a moving branch; the version string alone does not identify the patch stack.

The design follows the local Python builder's separation of build recipes, locked inputs, manifests and an independent lab. It also follows the [original PHP builder's](https://github.com/Lewiscowles1986/php-wasm-builder) Buildx/local-export model. Neither existing repository is modified by this work.

Primary upstream references: [OTP](https://github.com/erlang/otp/tree/e07fd07837e5aa845657f5fa340637121e451d47), [Popcorn](https://github.com/software-mansion/popcorn/tree/bea24dd50fec39a5859e49c54d496736a3c6857a), [Elixir releases](https://github.com/elixir-lang/elixir/releases), and [Emscripten](https://emscripten.org/docs/compiling/WebAssembly.html).
