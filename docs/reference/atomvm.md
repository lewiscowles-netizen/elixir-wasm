# AtomVM integration reference

| Property | Value |
| --- | --- |
| CLI selector | `--backend atomvm` |
| Runtime | Stock AtomVM 0.6.6 |
| Source commit | `ff993a80963298b532c1e573f883951ecaac9fef` |
| Source and compiler pins | `families/backends.lock.json` |
| Configured Elixir compiler line | 1.17; first/latest locked releases |
| Native compiler OTP | 26.2.5.13 |
| Browser execution | Precompiled BEAM program; no source evaluation |
| Runtime libraries | AtomVM's `atomvmlib`, including its Elixir subset |
| Entry point | Generated `AtomVMLab.start/0` |
| Program input | `--script <path>`, default `examples/atomvm/hello.exs` |
| Output directory | `builds/atomvm-<version>` |
| Project bundling | Not implemented for this backend |
| Popcorn dependency | None |
| WASI | Separate [adapted command profile](wasi.md), with independent host evidence |

The selected Elixir release identifies the compiler, not a complete Elixir standard library available at runtime. `System.version/0`, `Code.eval_string/3`, Mix, dynamic compilation, full OTP applications and arbitrary Hex packages must not be assumed available. The packaged script must use AtomVM-supported calls.

The browser recipe adds Emscripten module/export options so the lab can preload `.avm` files into a fresh worker. Source and library archives are checksum-verified. The emitted manifest identifies `AtomVM.wasm`, `AtomVM.mjs`, `program.avm`, `atomvmlib.avm`, source, licenses and native probe output. `otp` is null because the browser VM is AtomVM.

See the [measured integration matrix](backends.md). Primary sources: [AtomVM 0.6.6](https://github.com/atomvm/AtomVM/tree/ff993a80963298b532c1e573f883951ecaac9fef), its [Emscripten build instructions](https://github.com/atomvm/AtomVM/blob/ff993a80963298b532c1e573f883951ecaac9fef/doc/src/build-instructions.md#building-for-emscripten), and [Elixir library subset](https://github.com/atomvm/AtomVM/tree/ff993a80963298b532c1e573f883951ecaac9fef/libs/exavmlib/lib).
