# Build selected versions

Install Python 3.9 or later and Docker with Buildx. Run commands from the builder repository. The lab is a separate sibling repository.

This guide uses the default `--backend direct` route. For the other integrations, use the [Popcorn](popcorn.md) or [AtomVM](atomvm.md) build guide; their compiler ranges and execution contracts differ.

Inspect the final export plan before starting:

```sh
python3 scripts/build.py 1.20.4 --print
```

Build one exact release, the endpoints of one minor, or the complete catalogue:

```sh
python3 scripts/build.py 1.20.4
python3 scripts/build.py 1.19
python3 scripts/build.py --all --parallel 2
```

The coordinator automatically chooses a pinned historical compiler for releases before 1.20, preserves their Erlang abstract forms, and recompiles those forms for the modern browser VM. See the [historical family reference](../reference/historical-families.md) for transformations and limitations. Elixir 1.20 compiles directly with OTP 29.

Browser builds first cache their packaging stage, then export the final scratch target in a second Buildx invocation. This sequencing avoids a five-minute inter-stage pause observed with the local BuildKit 0.33 installation. Both phases reuse the same recipe and inputs; phase durations and exit codes are recorded with the build result.

Every attempted version gets a result and full log under `builds/logs/`. A failure does not stop other selections. The command exits nonzero if any selection failed. `--parallel` limits concurrent versions; `--jobs` controls the modern compiler and shared runtime build, while historical compilers use two jobs. Keep `--jobs` unchanged between builds to reuse the runtime layer.

To test compilation separately from runtime packaging:

```sh
python3 scripts/build.py 1.0.0 --target compiler
python3 scripts/build-historical.py 1.0 --native-only
```

The first command deliberately tests against OTP 29 and can fail for historical sources. The second uses the matching historical compiler and preserves its native version/arithmetic probe. Neither command establishes browser support.

After a browser build succeeds, verify and import it:

```sh
python3 scripts/export-lab.py ../elixir-wasm-lab builds/browser-1.20.4
```

Start the lab with its `serve.py` and run the acceptance suite described in the lab README. Keep fresh evidence whenever runtime bytes change. Do not promote an untested build by editing its status.

The supported Docker output is a local directory. Docker's host architecture selection is independent of the Emscripten output target. Use the same lock files and source archives when comparing hosts.
