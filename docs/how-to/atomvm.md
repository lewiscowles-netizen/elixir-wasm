# Build an AtomVM program

Use the stock AtomVM recipe for a script that fits AtomVM's library subset. The builder compiles the program before browser startup.

```sh
python3 scripts/build.py 1.17.3 --backend atomvm --script examples/atomvm/hello.exs
python3 scripts/export-lab.py ../elixir-wasm-lab builds/atomvm-1.17.3
```

Omit `--script` to use the example. Select `1.17` to build its first and latest locked releases. Other compiler lines are rejected until they have their own configured route; the direct backend's broad version matrix is not AtomVM evidence.

The script becomes the body of `AtomVMLab.start/0`. Return `:ok` for successful completion. The builder records the source, wraps it with a compiler-version probe, compiles it into BEAM bytecode and creates `program.avm`. It builds AtomVM's own Erlang/Elixir libraries into `atomvmlib.avm` and requires a native execution probe to succeed before exporting.

The browser VM is built independently from the same pinned AtomVM source using Emscripten. A small visible adjustment exports an ES module and filesystem-loading methods. It does not add Popcorn code or transplant OTP's standard library.

After import, select **AtomVM**. The source is read-only because editing text cannot change the already compiled program. Rebuild and reimport whenever the source changes.

Run the supplied example's browser probe from the lab:

```sh
yarn test:e2e --grep 'execute atomvm'
```

Those assertions describe `examples/atomvm/hello.exs`. Replace them with meaningful output assertions for your own script; a custom program should not be expected to print the example's greeting. See the [reference](../reference/atomvm.md) for unsupported features.
