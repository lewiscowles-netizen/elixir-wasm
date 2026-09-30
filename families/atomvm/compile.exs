source = File.read!("/program/source.exs")
version = System.version()
wrapped = "defmodule AtomVMLab do\n def start do\n IO.puts(\"COMPILER=#{version}\")\n" <> source <> "\n end\nend\n"
for {module, beam} <- Code.compile_string(wrapped, "/program/source.exs") do
  File.write!("/program/#{module}.beam", beam)
end
