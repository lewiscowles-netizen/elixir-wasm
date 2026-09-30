-module(lab_runner).
-export([start/0]).

start() ->
    case application:ensure_all_started(elixir) of
        {ok, _} -> run();
        Error -> io:format(standard_error, "Elixir startup failed: ~p~n", [Error]), erlang:halt(1)
    end.

run() ->
    {ok, Source} = file:read_file("/main.exs"),
    try 'Elixir.Code':eval_string(Source, [], []) of
        {Value, _Binding} ->
            Text = 'Elixir.Kernel':inspect(Value),
            io:format("~n=> ~ts~n", [Text]),
            erlang:halt(0)
    catch
        Kind:Reason:Stack ->
            io:format(standard_error, "~p: ~p~n~p~n", [Kind, Reason, Stack]),
            erlang:halt(1)
    end.
