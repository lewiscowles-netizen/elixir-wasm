# Run and debug on a closed network

Separate execution preparation from rebuild preparation. Running the browser lab needs its static assets. Rebuilding also needs source archives, container images, build dependencies and any application dependencies.

## Prepare browser execution

On a connected machine, build and export the selected runtimes. Copy the complete lab directory, including `web/runtimes/` and `web/runtimes.local.json`, to the closed network. These generated files are ignored by Git, so a source clone is insufficient.

Start `python3 serve.py` there. Open `http://127.0.0.1:8130/web/`. The built-in loader uses local runtime files and examples; it has no CDN or Hex download step. User-written network requests still need reachable endpoints.

In browser developer tools, inspect the Network panel after clearing the cache. Every application asset should come from the lab origin. A useful offline acceptance test blocks all other origins and runs version, arithmetic, module and filesystem examples in a fresh browser context.

## Diagnose loading

```sh
curl -I http://127.0.0.1:8130/web/
curl -I http://127.0.0.1:8130/web/runtimes.local.json
```

Check that the page includes both cross-origin isolation headers. Inspect the manifest link for the selected runtime, then fetch each named file. A proxy returning its login HTML with status 200 can look like a successful download until the Wasm or archive parser fails.

For an intranet hostname, use HTTPS with a certificate trusted by the browser. Plain HTTP on a non-localhost hostname is not equivalent to localhost. A reverse proxy must preserve headers on JavaScript, Wasm and filesystem responses. Serve `.wasm` as `application/wasm`.

The lab expects raw gzip archive bytes for `filesystem.tar.gz` and decompresses them explicitly. Do not also label that stored file with `Content-Encoding: gzip`; automatic HTTP decoding would cause double decompression.

## Prepare a rebuild

```sh
python3 scripts/fetch.py --all
python3 scripts/fetch.py --all --offline
```

The second command verifies the cached archives without downloading. Save the pinned images with Docker's image export tools and preserve a populated BuildKit cache or an internally mirrored toolchain image. Apt packages, Dockerfile frontend images and project dependencies need preparation too. `--offline` verifies source cache availability; it does not magically make an uncached Docker build independent of package repositories.

Use your organization's trusted CA and package mirrors. Do not disable TLS verification to work around a proxy. The current project recipe validates local `path:` dependencies. Hex support would additionally require pinned package-manager tooling and a dependency-resolution stage; an existing `deps/` directory alone is insufficient. See the [project tutorial](../tutorials/03-project.md).
