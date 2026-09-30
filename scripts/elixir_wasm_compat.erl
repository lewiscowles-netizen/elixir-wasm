-module(elixir_wasm_compat).
-export([normalize/1]).

normalize(Tree) ->
    erl_parse:map_anno(fun
        (Line) when is_integer(Line), Line < 0 -> erl_anno:set_generated(true, erl_anno:new(-Line));
        (Annotation) -> Annotation
    end, Tree).
