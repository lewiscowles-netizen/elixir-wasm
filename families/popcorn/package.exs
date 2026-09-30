root = "/bundle/fs/lib"
popcorn = root <> "/popcorn/ebin"
lab = root <> "/popcorn_lab/ebin"
File.mkdir_p!(popcorn)
File.mkdir_p!(lab)
{:ok, modules, _} = Kernel.ParallelCompiler.compile_to_path(Path.wildcard("/src/popcorn/popcorn/elixir/lib/**/*.ex"), popcorn)
{:ok, lab_modules, _} = Kernel.ParallelCompiler.compile_to_path(["/builder/recipe/popcorn_lab.ex"], lab)
for {app, dir, version, app_modules, dependencies, start} <- [
  {:popcorn, popcorn, "0.4.0-next.0", modules, [:kernel, :stdlib, :elixir, :logger], Popcorn.Application},
  {:popcorn_lab, lab, "0.0.0", lab_modules, [:kernel, :stdlib, :elixir, :logger, :popcorn], PopcornLab}
] do
  properties = [vsn: String.to_charlist(version), modules: app_modules, applications: dependencies, registered: [], mod: {start, []}]
  File.write!(dir <> "/#{app}.app", :io_lib.format(~c"~p.~n", [{:application, app, properties}]))
end
