# Prepare a portable browser lab

Build and import the exact versions you want to distribute using [the build guide](build.md). In the lab repository, render the exported documentation and test the selected bundles:

```sh
yarn install --frozen-lockfile
yarn docs:build
yarn test:e2e
python3 scripts/package-lab.py
```

The archive at `dist/elixir-wasm-lab.tar.gz` contains the selected runtime bundles, UI, rendered documentation, evidence, source documentation and a Python static server. Its neighboring `.sha256` file identifies the exact archive. Packaging verifies every selected runtime file against its manifest and rejects changed bytes. Old runtime directories no longer referenced by the catalogue are excluded.

On another machine, extract the archive, enter `elixir-wasm-lab` and run:

```sh
python3 serve.py
```

Open `http://127.0.0.1:8130/web/`. Running the exported lab needs Python 3.9 or later and a compatible browser; Node, Yarn, Docker and an AI service are not runtime dependencies. Documentation and runtime files are served locally. See [closed networks](offline.md) for remote hosting headers and cache preparation.

To regenerate documentation after changing the builder's Markdown, re-export a bundle to refresh `docs/`, then run `yarn docs:build`. The builder remains the documentation source; do not edit the generated lab copy.
