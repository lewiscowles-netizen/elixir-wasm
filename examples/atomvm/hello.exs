IO.puts("Hello from stock AtomVM")
:erlang.display({:squares, Enum.map([1, 2, 3], fn n -> n * n end)})
parent = self()
spawn(fn -> send(parent, {:answer, 6 * 7}) end)
receive do
  {:answer, value} -> IO.puts("MESSAGE=" <> Integer.to_string(value))
after
  1000 -> :erlang.error(:timeout)
end
:ok
