# AtomVM WASI command reference

| Property | Contract |
| --- | --- |
| Build selection | `--backend atomvm --target wasi` |
| Artifact target | `wasm32-wasip1`; WASI Preview 1 command, not a component |
| Runtime | AtomVM 0.6.6 with this repository's WASI platform adaptation |
| Elixir compiler endpoints | 1.17.0 and 1.17.3, native OTP 26.2.5.13 |
| Toolchain | wasi-sdk 34, pinned archives in `families/wasi/toolchain.lock.json` |
| Recorded execution host | Wasmtime 49.0.1 |
| Imports | Only functions from `wasi_snapshot_preview1` |
| VM entrypoint | `_start`; first packbeam program's `start/0` |
| Scheduler | One scheduler; Elixir processes and message passing remain available |
| Memory | Maximum 256 MiB linear memory; 1 MiB C stack; current build uses `-Os` |
| Time | Realtime and monotonic clocks, timers; local time is UTC; timezone argument rejected |
| Files | Explicit host preopens, through AtomVM `posix_*` APIs |
| Unsupported | Runtime Elixir compilation, full OTP/Mix libraries, sockets, distribution, subprocesses, dynamic native libraries, crypto/TLS |
| Program exit | `:ok` returns host exit 0; other return values and uncaught errors fail |

Each bundle contains `AtomVM.wasm`, `program.avm`, `atomvmlib.avm`, `source.exs`, licenses, notices and `manifest.json`. Independent acceptance packs `probe.avm`, `failure.avm` and `loop.avm` include their corresponding `.exs` sources. Native smoke output is a compiler-stage check, not WASI evidence.

The [host evidence](../evidence/wasi.json) binds each result to a manifest hash, host version and executable hash. The exporter verifies every artifact hash and the WASI import namespace before it creates a separate `wasi-atomvm-VERSION` catalogue entry and download archive. Browser bundles cannot satisfy this contract merely by changing their target label.

This measured scope covers the included probes, not all Elixir or AtomVM APIs. Direct OTP and Popcorn have no WASI recipe. See [target comparison](targets.md) and the [port explanation](../explanation/wasi.md).
