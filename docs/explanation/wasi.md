# Why the WASI port uses a separate AtomVM platform

The browser work established the Elixir compiler, bytecode and runtime boundaries first. The WASI work changes the host contract while preserving those boundaries: native Elixir produces BEAM bytecode, and a WebAssembly VM executes that bytecode. Neither route embeds Python as a language runtime.

AtomVM makes the first WASI port tractable because its interpreter and platform APIs are smaller than full OTP. The pinned source has a Unix platform and an Emscripten platform. This builder adapts the Unix platform to WASI Preview 1, using wasi-libc for clocks, polling and file descriptors. Packbeam loading copies files into linear memory instead of using Unix memory mapping.

A single scheduler avoids native thread and signal requirements while preserving lightweight Elixir processes. Socket drivers, dynamic library loading and timezone database behavior are excluded. These are declared limits of this port, not capabilities inferred from the browser build. The compiler uses size optimization (`-Os`); unoptimized interpreter code exceeds WebAssembly local-variable limits.

Preopened directories define the filesystem boundary. Wasmtime can load `AtomVM.wasm` without granting that module access to its containing directory. The VM needs an explicit grant to read its BEAM packs, and a separate grant for application data. The acceptance fixture includes a real file outside the granted data directory and a symlink pointing to it, so the negative cases exercise the host boundary rather than merely checking a missing file.

Evidence therefore has two parts: import inspection establishes the declared ABI, and host execution establishes the behavior observed for these programs. A `wasm32-wasip1` artifact is a command module, not a Preview 2/3 component. See the [WASI SDK](https://github.com/WebAssembly/wasi-sdk), [Wasmtime CLI documentation](https://docs.wasmtime.dev/cli-options.html), and the [measured capability reference](../reference/wasi.md).
