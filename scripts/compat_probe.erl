-module(compat_probe).
-export([run/0]).
run() ->
    {ok, _} = application:ensure_all_started(elixir),
    Source = <<"IO.puts(System.version()); IO.inspect(Enum.map([1,2,3], fn n -> n*n end)); defmodule BrowserProof do\n def answer, do: 42\nend\np = self(); spawn(fn -> send(p, {:ok, 42}) end); receive do {:ok, n} -> IO.inspect(n) after 1000 -> raise \"timeout\" end; File.write!(\"/tmp/probe.txt\", \"file\"); IO.puts(File.read!(\"/tmp/probe.txt\")); BrowserProof.answer()">>,
    {42, _} = 'Elixir.Code':eval_string(Source, [], []),
    io:format("COMPAT_PROBE_PASS~n"),
    halt(0).
