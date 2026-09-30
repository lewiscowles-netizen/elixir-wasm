# Provenance notice

This is an independent Elixir implementation of the build-and-lab pattern used by the local Python WebAssembly repositories and the original PHP WebAssembly builder. Their source repositories remain unchanged.

The browser VM is Erlang/OTP with the pinned Software Mansion Popcorn patch stack. Their copyright and license texts travel with exported bundles. The historical retargeting experiment is a local compatibility experiment and is not an upstream-supported OTP combination.

Exact input identities are recorded in `sources.lock.json`, `versions.json`, and the historical Dockerfile. Generated outputs include their file hashes and upstream licensing material.
