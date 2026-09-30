# Why use the Popcorn integration?

Popcorn supplies the application-facing bridge between browser JavaScript and BEAM processes. The lab's Popcorn route uses its actual JavaScript SDK, Elixir modules and proxy process. Selecting it changes how the VM boots, how source reaches Elixir, and how calls return to the page.

The direct route writes source into a temporary filesystem and starts a small Erlang runner. Popcorn instead boots an OTP application with a supervisor. The frontend calls its registered evaluator through the SDK's GenServer interface. Elixir can call JavaScript in the other direction through `Popcorn.Wasm.run_js!/1`.

That bridge is useful when the browser and Elixir application collaborate over time: UI events become messages, named processes own state, and replies update the page. The current lab deliberately restarts the VM for every run to keep examples independent. A persistent application would make a different lifecycle choice while keeping the same upstream APIs.

Popcorn's architecture is version-dependent. The selected 0.4 prerelease uses a patched OTP VM. Earlier Popcorn work used a modified AtomVM. Consequently, “Popcorn versus AtomVM” is not a universal distinction between mutually exclusive technologies. This lab names the exact integration and VM in its manifests and [compatibility reference](../reference/backends.md).

Choose Popcorn when those browser APIs are part of the application you want to build. Choose the [direct OTP API](direct-otp.md) when evaluating scripts through a small host adapter is sufficient. Choose [stock AtomVM](atomvm.md) for a compiled program whose needs fit its smaller runtime.
