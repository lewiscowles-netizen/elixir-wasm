IO.puts("Hello from Elixir on WASI")
:erlang.display({:platform, :atomvm.platform()})
:erlang.display({:squares, Enum.map([1, 2, 3], fn n -> n * n end)})
parent = self()
spawn(fn -> send(parent, {:answer, 6 * 7}) end)
receive do
  {:answer, value} -> IO.puts("MESSAGE=" <> Integer.to_string(value))
after
  1000 -> :erlang.error(:message_timeout)
end
started = :erlang.monotonic_time(:millisecond)
:erlang.send_after(25, self(), :timer)
receive do
  :timer -> IO.puts("TIMER_MS=" <> Integer.to_string(:erlang.monotonic_time(:millisecond) - started))
after
  1000 -> :erlang.error(:timer_timeout)
end
case :atomvm.posix_open("/data/input.txt", [:o_rdonly]) do
  {:ok, file} ->
    {:ok, contents} = :atomvm.posix_read(file, 1024)
    :ok = :atomvm.posix_close(file)
    IO.puts("FILE=" <> contents)
  {:error, _} -> IO.puts("FILE=denied")
end
for path <- ["/data/../outside.txt", "/data/escape.txt"] do
  case :atomvm.posix_open(path, [:o_rdonly]) do
    {:ok, file} ->
      :atomvm.posix_close(file)
      :erlang.error(:filesystem_escape)
    {:error, _} -> IO.puts("ESCAPE=denied")
  end
end
:ok
