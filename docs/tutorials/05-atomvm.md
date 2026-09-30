# Run a compiled Elixir script on AtomVM

You will compile an Elixir script with a native compiler, then execute its bytecode on stock AtomVM in the browser. This exercise uses Elixir 1.17.3 as the compiler.

From the builder repository:

```sh
python3 scripts/build.py 1.17.3 --backend atomvm
python3 scripts/export-lab.py ../elixir-wasm-lab builds/atomvm-1.17.3
```

Start the lab, select **AtomVM**, then **1.17.3**. The editor shows the bundled source and is read-only. Press **Run Elixir**. The output includes:

```text
COMPILER=1.17.3
Hello from stock AtomVM
{squares,[1,4,9]}
MESSAGE=42
```

The compiler version is captured during compilation. AtomVM supplies its own supported library subset; this is not a full Elixir 1.17 installation running on OTP.

Create `hello-atomvm.exs` in your working directory:

```elixir
IO.puts("My browser program")
:erlang.display(7 * 8)
:ok
```

Build and reimport it:

```sh
python3 scripts/build.py 1.17.3 --backend atomvm --script hello-atomvm.exs
python3 scripts/export-lab.py ../elixir-wasm-lab builds/atomvm-1.17.3
```

Reload the lab. Its read-only source now matches your program, which prints `56`. The changed bundle replaces the selected AtomVM entry and needs fresh browser evidence. Read [AtomVM's compatibility boundary](../reference/atomvm.md) before adding dependencies.
