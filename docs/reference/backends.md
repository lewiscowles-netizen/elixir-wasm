# Runtime integrations

The backend selects a runtime and application interface. The execution target selects a host contract; all three integrations have browser recipes. AtomVM also has a separate [WASI command target](wasi.md), with [host execution evidence](../evidence/wasi.json). The counts below cover browser execution only.

| Backend | Application interface | Elixir selection means | Measured browser bundles |
| --- | --- | --- | --- |
| [Direct OTP](../explanation/direct-otp.md) | Small script runner; attributed Popcorn VM patches | Compiler and bundled Elixir libraries | 43/43 passed |
| [Popcorn](popcorn.md) | Upstream JavaScript SDK and Elixir GenServer bridge | Compiler and bundled Elixir libraries | 2/2 passed |
| [AtomVM](atomvm.md) | Stock runtime; precompiled program | Native compiler; AtomVM supplies its own library subset | 2/2 passed |

Counts include application variants. The [direct release matrix](validation.md) separately lists its 42 locked release endpoints. Historical retargeting is specific to that route. Compatibility is not inherited by a new backend merely because its version dropdown contains the same source catalogue.

| Integration bundle | Chromium result |
| --- | --- |
| atomvm-1.17.0 | passed |
| atomvm-1.17.3 | passed |
| popcorn-1.20.0 | passed |
| popcorn-1.20.4 | passed |

The [machine-readable evidence](../evidence/backends.json) records exact manifest hashes. Browser tests also cover a JavaScript round trip and lifecycle/error handling for Popcorn, and read-only source plus the compiled example for AtomVM. An unavailable release stays disabled in the UI. The CLI rejects unconfigured compiler families before Docker runs.

Choose an integration with `--backend direct`, `--backend popcorn` or `--backend atomvm`. Each exports to a distinct catalogue identity, so importing one cannot replace another backend at the same Elixir version. See the [Popcorn build guide](../how-to/popcorn.md) and [AtomVM build guide](../how-to/atomvm.md).
