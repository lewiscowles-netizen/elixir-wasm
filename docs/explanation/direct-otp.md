# What the direct OTP option means

The direct option uses a small browser adapter and an Erlang runner. User programs do not start a Popcorn application or use its JavaScript SDK, proxy processes or Elixir application APIs. AtomVM is not involved.

The VM still comes from OTP with the pinned Popcorn portability patches. Those patches provide the low-level browser port, including Emscripten integration. Packaging also applies the attributed BEAM library fixes. “No framework API” describes the application interface; it does not claim an independently developed, unmodified OTP WebAssembly port.

This distinction lets the builder reuse a working VM while offering two application interfaces: a direct script runner and the fuller [Popcorn integration](popcorn.md). Their shared VM lineage is visible in source locks and manifests. A completely independent OTP port with no Popcorn code remains separate engineering work.

The direct adapter has the broadest measured release coverage because it can use the historical retargeting pipeline without requiring each old Elixir release to compile modern framework modules. Its [release matrix](../reference/validation.md) covers the script probes; it does not establish full standard-library or historical OTP fidelity.

Use this route for version comparisons, editable scripts and the existing Mix project tutorial. The [runtime integration reference](../reference/backends.md) separates its evidence from stock AtomVM and the Popcorn SDK.
