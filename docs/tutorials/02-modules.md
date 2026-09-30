# Grow a script into collaborating modules

This tutorial builds on [your first script](01-script.md). You will define a module, start a process and receive its answer.

Paste this into an available browser runtime:

```elixir
defmodule Calculator do
  def square(number), do: number * number
end

parent = self()
spawn(fn -> send(parent, {:result, Calculator.square(12)}) end)

receive do
  {:result, value} -> IO.inspect(value)
after
  1000 -> raise "No result arrived"
end
```

Run it. You should see `144`. The browser hosts one Wasm VM; `spawn/1` creates a BEAM process inside that VM. It does not create a Docker container or operating-system process.

Change `12` to another integer and repeat. The module is compiled by the selected Elixir compiler inside the VM.

Now try a temporary file:

```elixir
File.write!("/tmp/result.txt", "144")
File.read!("/tmp/result.txt")
```

The result is `"144"`. Run only the second line in a fresh run. It fails because the earlier filesystem no longer exists. This gives you a useful boundary: explicitly pass durable state into a new run instead of assuming the browser VM owns your disk.

The next step is [bundling a Mix project](03-project.md), which moves compilation of project modules to build time and packages their dependencies.
