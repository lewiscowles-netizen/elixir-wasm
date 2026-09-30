# Run your first browser script

You will run a small Elixir expression, then ask the runtime which Elixir release it actually loaded. Use an exported browser build; see [build selected versions](../how-to/build.md) if the lab contains none.

From the sibling lab repository, start its static server:

```sh
python3 serve.py
```

Open `http://127.0.0.1:8130/web/`. Keep **Direct OTP · no framework API** selected, choose an available Elixir release and keep **Browser · Emscripten** selected. The page should report that WebAssembly threads are ready.

Enter:

```elixir
IO.puts("Elixir " <> System.version())
6 * 7
```

Press **Run Elixir**. Standard output should contain the selected Elixir version and `=> 42`. The server only delivered files: evaluation happened in your browser.

Change the final expression to:

```elixir
Enum.map([1, 2, 3], fn n -> n * n end)
```

Run again. The result should be `[1, 4, 9]`. Each run starts a fresh VM, so variables and files from the previous run are gone.

Select a second available release and repeat the version check. Catalogue entries without bundles cannot run until their matching artifacts are imported; the runtime details separately show whether browser tests passed. The reported version comes from Elixir itself; it is not supplied by the dropdown.

Choose **Errors & recovery**, run it, then return to the first example. You should see a failed run followed by a successful fresh run. Continue with [modules and processes](02-modules.md).
