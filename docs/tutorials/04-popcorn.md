# Evaluate code through Popcorn

You will run Elixir through Popcorn's JavaScript SDK, then call JavaScript from that Elixir code. Start with the running lab and its imported `popcorn-1.20.4` bundle. If it is missing, follow [Build the Popcorn integration](../how-to/popcorn.md).

Select **Popcorn** under **Runtime integration**, then **1.20.4**. Replace the editor contents with:

```elixir
IO.puts("Elixir " <> System.version())
answer = Popcorn.Wasm.run_js!("() => 6 * 7")
IO.puts("JavaScript returned #{answer}")
answer
```

Press **Run Elixir**. The output includes `JavaScript returned 42` and `=> 42`.

The page boots the actual Popcorn SDK and sends your source through `popcorn.genserver.call("lab_evaluator", ["eval", source])`. A supervised Elixir process evaluates it. `Popcorn.Wasm.run_js!/1` then makes the reverse trip to JavaScript and returns the result to Elixir.

Change the JavaScript expression to `6 * 8` and run again. Both results become `48`. Each run creates a fresh VM, so earlier module definitions and files do not survive.

Next, try the **Errors & recovery** example. A failed evaluation appears on standard error, and another run still works. Read [how Popcorn fits](../explanation/popcorn.md) before adapting the SDK to a persistent application.
