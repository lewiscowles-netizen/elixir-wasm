# Historical compiler families

Elixir and Erlang/OTP versions are independent. First and latest patches can have different OTP compatibility; `1.0.0` and `1.0.5` are not interchangeable build inputs.

The [upstream compatibility reference](https://elixir.hexdocs.pm/compatibility-and-deprecations.html) is the authority for supported native pairs. The current browser runtime is OTP 29. A successful older-source compilation on OTP 29 is an experimental result, not a statement of upstream support.

| Elixir group | Native compiler generation | Packaging route |
| --- | --- | --- |
| 1.0–1.1 | OTP 17.5 | Historical retargeting |
| 1.2–1.5 | OTP 18.3 | Historical retargeting |
| 1.6 | OTP 19.3 | Historical retargeting |
| 1.7–1.13 | OTP 22.3.4.26 | Historical retargeting |
| 1.14–1.16 | OTP 24.3.4.17 | Historical retargeting |
| 1.17–1.19 | OTP 26.2.5.13 | Historical retargeting |
| 1.20 | OTP 29.0.6 | Direct compilation |

These groups describe compiler pairings, not proven browser compatibility. The native VM executable does not run inside a browser. Compiled bytecode still needs a compatible Wasm VM, and runtime compilation depends on OTP compiler internals.

Legacy Rebar compilation uses one worker. Parallel Rebar jobs stalled on 1.4.0 and 1.5.0 during this build; serial compilation successfully progressed through the same source. Make itself retains the two-job limit.

The `historical-browser-artifacts` experiment recompiles preserved abstract code using modern OTP. It records that transformation and deliberately does not claim to recreate the original OTP runtime. Full historical fidelity would require porting the matching OTP generation or validating an alternative interpreter's behavior.

The matching compiler extracts Erlang abstract forms before export, so the retargeter does not depend on newer Elixir understanding older Elixir debug metadata. Retargeting removes old type/spec/callback attributes rejected by OTP 29, strips record field types while retaining their fields and defaults, and normalizes negative generated-code annotations. Calls into the Erlang compiler and evaluator also normalize annotations generated at runtime. The Elixir application's unconditional crypto startup dependency is removed; crypto calls remain unavailable. Runtime compilation of old type specifications, removed OTP functions and stored regular expressions can still fail; passing the core probes does not establish complete standard-library compatibility.

The 1.0.0 compiler experiment uses a visible `stdio.patch` to replace the obsolete stderr Unicode option with `encoding=utf8`. Source archives retain their original checksums. No checksum is updated to conceal a local patch.
