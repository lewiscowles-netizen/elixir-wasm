version = System.version()
for {name, source} <- [
  {"probe", File.read!("/builder/probe.exs")},
  {"failure", ":erlang.error(:intentional_wasi_failure)"},
  {"loop", "IO.puts(\"LOOP_STARTED\")\ndefmodule WASILoop do\n def run, do: run()\nend\nWASILoop.run()"}
] do
  directory = "/probes/" <> name
  File.mkdir_p!(directory)
  wrapper = "defmodule WASIProbe do\n def start do\nIO.puts(\"COMPILER=#{version}\")\n" <> source <> "\n end\nend\n"
  modules = Code.compile_string(wrapper)
  for {module, bytes} <- modules, do: File.write!("#{directory}/#{module}.beam", bytes)
  beams = ["#{directory}/Elixir.WASIProbe.beam" | Path.wildcard("#{directory}/*.beam") -- ["#{directory}/Elixir.WASIProbe.beam"]]
  {_, 0} = System.cmd("/src/atomvm/build/tools/packbeam/PackBEAM", ["/probes/#{name}.avm" | beams])
  File.write!("/probes/#{name}.exs", wrapper)
end
