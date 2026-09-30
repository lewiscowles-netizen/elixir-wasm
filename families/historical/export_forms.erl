-module(export_forms).
-export([run/0]).

run() ->
    Paths = filelib:wildcard("lib/*/ebin/*.beam"),
    lists:foreach(fun(Path) ->
        case beam_lib:chunks(Path, [abstract_code]) of
            {ok, {_, [{abstract_code, {raw_abstract_v1, Forms}}]}} ->
                ok = file:write_file(Path ++ ".forms", term_to_binary(Forms, [compressed]));
            Failure -> erlang:error({cannot_preserve_abstract_forms, Path, Failure})
        end
    end, Paths),
    io:format("Preserved abstract forms for ~p modules~n", [length(Paths)]),
    halt(0).
