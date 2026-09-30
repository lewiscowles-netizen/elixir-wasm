#!/bin/sh
set -eu
mkdir -p /src/selected-elixir
cp -r /input/lib /src/selected-elixir/lib
/src/tools/bin/elixir /builder/recompile-historical.exs
cp -r /src/selected-elixir/lib /output/
erlc -o /output /builder/compat_probe.erl
erl -noshell -pa /output /src/selected-elixir/lib/elixir/ebin -s compat_probe run
