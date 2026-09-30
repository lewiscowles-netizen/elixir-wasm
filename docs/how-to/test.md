# Verify a browser build

Import a bundle with `scripts/export-lab.py`, then run these commands in the lab repository:

```sh
yarn install --frozen-lockfile
yarn exec playwright install chromium
yarn test:e2e
```

The suite starts the loopback server when needed and executes every imported bundle in Chromium. The OTP routes check actual Elixir/OTP versions, arithmetic, dynamic modules, processes, files and output streams, plus JSON round trips on Elixir 1.18 and later. Popcorn also checks an Elixir-to-JavaScript bridge round trip. AtomVM checks its precompiled example's compiler identity, arithmetic and messages, and verifies that its source editor is read-only. The sample `receipts` project additionally checks application startup, its local dependency, GenServer state and a bundled `priv/` file. Other programs need their own probes. Lifecycle tests check errors, fresh state and stopping/restarting both editable backends. External HTTP requests are blocked for each bundle probe.

`evidence/browser.json` records test outcomes, browser version, output and each tested manifest's SHA-256. A passing record applies only to those bytes. Reimporting a different artifact makes old evidence inapplicable; run the suite again. A successful compiler or packager is not a browser pass. The suite covers a defined core, not every Elixir or OTP API.

Use `yarn test:e2e --grep 'execute 1.0.0 '` for a focused investigation. A filtered run's evidence covers only that selection, so run the complete suite before producing a full compatibility report. Playwright preserves traces for failures under `test-results/`.

Check the builder's source-selection and bundle-integrity contract separately:

```sh
python3 -m unittest discover -s tests -v
```

These checks reject changed assets, unsafe manifest paths and accidental use of a browser recipe for WASI. For import-level inspection, run `node scripts/inspect-wasm.mjs builds/browser-1.20.4/beam.wasm`; an import listing is evidence about host requirements, not execution success.

After the full browser suite, regenerate both reports from the builder repository with `python3 scripts/report-validation.py` and `python3 scripts/report-backends.py`. Re-export a bundle and render the docs to make the current results visible in the lab.
