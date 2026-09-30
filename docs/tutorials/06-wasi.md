# Run your first Elixir WASI command

You will compile an Elixir script, execute it in Wasmtime, and grant it access to one directory. Start in the builder repository with Docker Buildx, Python 3.9 or newer, and [Wasmtime](https://docs.wasmtime.dev/cli-install.html) installed. The recorded host is Wasmtime 49.0.1.

Build the latest configured AtomVM compiler endpoint:

```sh
python3 scripts/build.py 1.17.3 --backend atomvm --target wasi
cd builds/wasi-atomvm-1.17.3
wasmtime run --dir .::/bundle AtomVM.wasm /bundle/program.avm /bundle/atomvmlib.avm
```

The program prints its compiler version, `{platform,wasi}`, square numbers, `MESSAGE=42`, and a timer duration. `FILE=denied` is expected: the VM can read its bytecode bundle, but you have not granted a data directory. Both escape attempts print `ESCAPE=denied`.

Create a directory and grant it separately:

```sh
mkdir -p data
printf 'Hello from a permitted directory' > data/input.txt
wasmtime run --dir .::/bundle --dir data::/data AtomVM.wasm /bundle/program.avm /bundle/atomvmlib.avm
```

The `FILE=` line now contains your text. `/data` is a guest path chosen by the host command. Elixir still runs inside WebAssembly; Python is not involved in either execution command.

Return to the builder root and inspect the source at `examples/wasi/hello.exs`. It uses AtomVM's file API because this runtime supplies a library subset. Next, [build your own script](../how-to/wasi.md), or read the [WASI capability reference](../reference/wasi.md).
