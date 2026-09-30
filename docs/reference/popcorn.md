# Popcorn integration reference

| Property | Value |
| --- | --- |
| CLI selector | `--backend popcorn` |
| Upstream | Popcorn `0.4.0-next.0`, source pin in the [provenance reference](provenance.md) |
| Runtime | OTP 29.0.6 with the pinned Popcorn port |
| Configured Elixir compiler line | 1.20; first/latest locked releases |
| Execution | Editable source evaluated inside the browser |
| Browser API | Actual upstream `Popcorn` JavaScript SDK |
| Application API | Upstream `Popcorn.Proxy` and `Popcorn.Wasm` |
| Lab entrypoint | `popcorn_lab`, with a supervised `lab_evaluator` GenServer |
| Protocol | `genserver.call("lab_evaluator", ["eval", source])` |
| Output directory | `builds/popcorn-<version>` |
| Project and script flags | Not supported by this recipe |
| WASI | Unimplemented; request rejected |

The reply to an evaluation contains string keys `ok` and either `value` or `error`. Results are inspected strings; the frontend does not receive arbitrary Elixir terms. Each lab run starts a new SDK instance and VM. Stop terminates the SDK's worker through `deinit()`.

Artifacts include `popcorn.mjs`, `popcorn-worker.mjs`, the OTP runtime, `vm.boot`, and separate application tar files. The manifest records the framework identity, file hashes and recipe hashes. The [integration matrix](backends.md) is the home for measured results.

This is prerelease upstream work. The browser profile's [runtime restrictions](targets.md) still apply. Using the SDK does not add a WASI implementation or restore omitted native libraries.

Primary source: [the pinned Popcorn SDK and Elixir implementation](https://github.com/software-mansion/popcorn/tree/bea24dd50fec39a5859e49c54d496736a3c6857a/popcorn). Popcorn 0.3's AtomVM-based architecture must not be confused with this selected OTP-based integration.
