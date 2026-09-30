# Bundle a Mix project and its dependency

You will compile the sample receipt project, include a local dependency and run its supervised process in the browser. Use Elixir 1.20.4 for this tutorial.

From the builder repository:

```sh
python3 scripts/build.py 1.20.4 --project examples/project --app receipts
python3 scripts/export-lab.py ../elixir-wasm-lab builds/project-receipts-1.20.4
```

The project has a `Receipts` module, a supervised `Receipts.Store` GenServer, a local `price_math` dependency and a text file under `priv/`. Buildx compiles the project with the selected Elixir toolchain and packages its application files alongside that runtime.

Start the lab and select the **receipts** entry. Paste:

```elixir
{:ok, _} = Application.ensure_all_started(:receipts)
IO.inspect(Receipts.remember([1200, 450, 350]))
IO.inspect(Receipts.remember([100, 200]))
IO.inspect(Receipts.history())
label = :code.priv_dir(:receipts) |> to_string() |> Path.join("receipt-label.txt")
IO.puts(File.read!(label))
```

Run it. Expected output includes `2000`, `300`, `[2000, 300]` and `A receipt from your browser`. The local dependency supplies the addition logic; the GenServer stores the two totals; the label comes from a bundled file.

Run it again. The history still contains only those two receipts because the lab starts a fresh VM each time.

To adapt your own project, pass its directory to `--project` and its OTP application name to `--app`. The validated dependency route uses local `path:` dependencies contained in that directory. The current compiler stage runs `mix compile`; it neither installs Hex nor fetches packages. Merely copying a Hex dependency into `deps/` does not install its package-manager tooling. Vendor dependencies as local paths for this recipe, or extend the build with a pinned dependency-resolution stage. It packages compiled `ebin` and `priv` directories and rejects attempts to overwrite runtime libraries.

Mix runtime configuration is not copied automatically. Call `Application.put_env/3` explicitly before `Application.ensure_all_started/1` for the sample boundary. A production application's configuration and startup contract require deliberate packaging. Read [project compatibility](../explanation/projects.md) before attempting a complete server release.
