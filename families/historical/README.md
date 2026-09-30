# Historical compiler experiment

This family builds early Elixir with an era-appropriate native OTP toolchain. Its native output is not itself a WebAssembly runtime.

Compiler images are pinned by digest in `compilers.json`. The [family reference](../../docs/reference/historical-families.md) maps release groups to compilers. The source checksum must be supplied from `versions.json`; there is no moving source download during the build.

The native export contains compiled libraries, their abstract forms, the upstream license and the actual native version/arithmetic probe. The `historical-browser-artifacts` stage uses those forms with OTP 29's compiler and records the [transformations](../../docs/reference/historical-families.md) in the artifact manifest.

The retargeting experiment is not a supported historical runtime until the actual browser probes pass. Missing abstract code or a compiler rejection fails the build rather than silently dropping modules. Removed OTP functions, changed compiler internals and regular-expression representations remain potential incompatibilities.

See the [version reference](../../docs/reference/versions.md) for evidence. Keep any successful limited probes distinct from a claim that the full old standard library works.
