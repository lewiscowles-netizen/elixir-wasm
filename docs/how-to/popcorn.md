# Build the Popcorn integration

Use this recipe when you need Popcorn's browser SDK and Elixir bridge APIs. For its exact pin and compatibility, consult the [Popcorn reference](../reference/popcorn.md).

Build one release or both endpoints of the configured compiler line:

```sh
python3 scripts/build.py 1.20.4 --backend popcorn
python3 scripts/build.py 1.20 --backend popcorn --parallel 2
```

Buildx reuses the OTP runtime and selected Elixir libraries. A separate pinned Node image bundles the upstream SDK using the committed Yarn lockfile. The packaging stage compiles the upstream Popcorn Elixir modules and the lab's supervised evaluator.

Import the resulting bundle:

```sh
python3 scripts/export-lab.py ../elixir-wasm-lab builds/popcorn-1.20.4
```

In the lab, select **Popcorn** and the imported release. Test it from the lab repository:

```sh
yarn test:e2e --grep popcorn
```

A focused run replaces the evidence file with that selection. Run the complete suite before publishing a combined compatibility report or portable archive.

The current recipe packages the lab evaluator, rather than arbitrary Popcorn Mix projects. `--project`, `--app` and `--script` are rejected for this integration. Use the direct backend's [project tutorial](../tutorials/03-project.md) for the existing project-bundling route. A custom Popcorn application also needs its own supervision tree, entrypoint and browser API contract.
