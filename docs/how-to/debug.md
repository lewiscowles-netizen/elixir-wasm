# Find the failing layer

Start with the earliest failure. A compiler failure, a missing browser asset and a missing application API have different fixes.

| Symptom | Check | Action |
| --- | --- | --- |
| Source checksum mismatch | Cached archive against the lock | Keep the lock; fetch the correct bytes |
| Native Elixir compile fails | `builds/logs/compiler-<version>.log` | Check source/OTP compatibility before touching Wasm |
| VM build fails | Buildx log, SDK identity, patch application | Reproduce the exact locked runtime recipe |
| Run button unavailable | Selected version, imported bundle, isolation status | Import a verified build or correct serving headers |
| Wasm fails to load | HTTP body, MIME type, complete import environment | Serve matching JS and Wasm from one bundle |
| VM never boots | Standard error, boot archive, OTP library versions | Verify bundle hashes and boot paths |
| `undef` in application code | Missing module/function or unsupported NIF | Include the dependency or adapt the call |
| File missing in a new run | VM lifecycle | Pass the file into the new instance explicitly |
| Run never ends | Infinite process or suspended browser | Stop it or let the configured deadline terminate the worker |

Use the smallest failing script. First test `System.version()`, then arithmetic, then the particular module. Record the selected runtime manifest and browser version with the failing source.

The **Errors & recovery** example intentionally fails. A fresh successful run afterwards checks that the failure did not leave state in the next VM. A successful arithmetic example alone does not establish support for a whole dependency tree.

For network-specific failures, follow [closed-network debugging](offline.md). For historical runtime issues, keep native compilation, bytecode loading and in-browser evaluation results separate in the [measured compatibility matrix](../reference/validation.md).
