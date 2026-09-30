# Elixir WebAssembly builder

A separate Elixir builder using the Python/PHP builders' pattern: locked sources, Docker Buildx, local artifact export, an independent browser lab, and evidence for each version. The catalogue selects the first and latest stable patch of every Elixir minor from 1.0 through 1.20.

This is an experimental port. See the [measured compatibility matrix](docs/reference/validation.md) for native compilation, browser packaging and browser execution results, and the [target reference](docs/reference/targets.md) for the browser/WASI boundary.

Three [runtime integrations](docs/reference/backends.md) are available: direct OTP without a framework API, Popcorn's actual SDK and Elixir bridge, and stock AtomVM for precompiled programs. Their supported compiler lines and runtime libraries differ; each has its own evidence and Diátaxis learning path.

## Interfaces

```sh
python3 scripts/build.py 1.20.4 --print
python3 scripts/build.py 1.20.4
python3 scripts/export-lab.py ../elixir-wasm-lab builds/browser-1.20.4
cd ../elixir-wasm-lab
python3 serve.py
```

Open `http://127.0.0.1:8130/web/`. The server serves static files; the code runs inside the browser. No assistant, AI service or remote compilation service is required.

## Repository map

| Path | Responsibility |
| --- | --- |
| `versions.json` | Exact first/latest stable release source archives and SHA-256 hashes |
| `sources.lock.json` | OTP, Popcorn patch stack, Autoconf and container identities |
| `Dockerfile` | Native compilation tools, Wasm runtime, selected Elixir and packaging stages |
| `scripts/` | Fetch, Buildx orchestration, packaging, verification and lab export |
| `examples/` | A Mix project with a local dependency, supervision and bundled files |
| `docs/` | Diátaxis documentation and validation evidence |
| `builds/`, `sources/`, `research/` | Ignored generated artifacts, cached inputs and investigations |

Start with the [documentation index](docs/README.md). The [architecture explanation](docs/explanation/architecture.md) distinguishes the native compiler, the Wasm VM, and the versioned Elixir bytecode.

The separate [WASI command target](docs/reference/wasi.md) uses AtomVM and a pinned WASI SDK. Start with the [WASI tutorial](docs/tutorials/06-wasi.md); Python orchestrates builds, while Elixir executes in the WebAssembly VM.
