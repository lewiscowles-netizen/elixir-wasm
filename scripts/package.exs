Code.require_file("/src/popcorn/popcorn/js/plugins/beam_tools/lib/popcorn/beam_tools/beam_patcher.ex")
root = "/bundle/fs"
File.mkdir_p!(root <> "/bin")
File.mkdir_p!(root <> "/lib/lab/ebin")
File.mkdir_p!(root <> "/home/web_user")
File.mkdir_p!(root <> "/tmp")
File.mkdir_p!(root <> "/etc")
File.write!(root <> "/etc/inetrc", "{lookup, [file]}.\n")
otp_root = to_string(:code.root_dir())
for app <- ["kernel", "stdlib", "compiler", "syntax_tools"] do
  [source] = Path.wildcard(otp_root <> "/lib/#{app}-*/ebin")
  File.mkdir_p!(root <> "/lib/#{app}")
  File.cp_r!(source, root <> "/lib/#{app}/ebin")
end
for source <- Path.wildcard("/src/selected-elixir/lib/*/ebin") do
  app = source |> Path.dirname() |> Path.basename()
  File.mkdir_p!(root <> "/lib/#{app}")
  File.cp_r!(source, root <> "/lib/#{app}/ebin")
end
for {app, module} <- [{"kernel", "prim_tty"}, {"stdlib", "beam_lib"}] do
  :ok = Popcorn.BeamTools.BeamPatcher.patch_beam(root <> "/lib/#{app}/ebin/#{module}.beam", "/src/popcorn/popcorn/js/plugins/beam_tools/patches/#{app}/#{module}.erl")
end
{:script, id, commands} = File.read!(otp_root <> "/bin/no_dot_erlang.boot") |> :erlang.binary_to_term()
commands = Enum.map(commands, fn
  {:path, dirs} -> {:path, Enum.map(dirs, fn dir -> Regex.replace(~r{/lib/([^/]+)-[^/]+/ebin}, to_string(dir), "/lib/\\1/ebin") |> String.to_charlist() end)}
  other -> other
end)
File.write!(root <> "/bin/vm.boot", :erlang.term_to_binary({:script, id, commands}))
{:ok, :lab_runner} = :compile.file(~c"/builder/lab_runner.erl", [{:outdir, String.to_charlist(root <> "/lib/lab/ebin")}, :debug_info, :report])
