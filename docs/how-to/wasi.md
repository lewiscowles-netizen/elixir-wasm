# Build and verify a WASI script

Use this guide to package your own precompiled Elixir program for a WASI Preview 1 command host. Prerequisites are the same as the [first WASI tutorial](../tutorials/06-wasi.md).

Write a script whose final value is `:ok`:

```elixir
IO.puts("My Elixir WASI program")
:ok
```

Build it with an exact release, or select both endpoints of the configured minor line:

```sh
python3 scripts/build.py 1.17 --backend atomvm --target wasi --script /absolute/path/hello.exs
```

The separate output directories are `builds/wasi-atomvm-1.17.0` and `builds/wasi-atomvm-1.17.3`. Compilation uses pinned native OTP; execution uses the WASI binary. Native smoke execution is also part of this recipe, so scripts should not depend unconditionally on a WASI-only environment during that check.

Run the independent acceptance programs and the selected script in a real host:

```sh
python3 scripts/verify-wasi.py builds/wasi-atomvm-1.17.* --wasmtime /absolute/path/wasmtime
```

The command writes `docs/evidence/wasi.json` and exits nonzero if a case fails. It verifies imports, filesystem grants and denial, process messages, timers, error propagation, and host fuel exhaustion. The selected script must finish successfully within 30 seconds.

Export the bundles and host evidence to the independent lab:

```sh
python3 scripts/export-lab.py ../elixir-wasm-lab builds/wasi-atomvm-1.17.*
cp docs/evidence/wasi.json ../elixir-wasm-lab/evidence/wasi.json
```

Select AtomVM and WASI in the lab to download a bundle and view its host command. This selection does not run a WASI polyfill in the browser. See [portable packaging](package-lab.md) to rebuild the full lab archive.
