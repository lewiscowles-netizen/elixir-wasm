# Direct compilation on OTP 29

The catalogue selects the first and latest stable patch of every released minor, starting at 1.0. Source pins, native compilation, browser packaging and browser execution are distinct states.

This is an OTP 29 compilation experiment, including combinations outside upstream support. Consult the [official compatibility table](https://elixir.hexdocs.pm/compatibility-and-deprecations.html) before interpreting a failure as an Elixir defect. Native compilation success alone does not prove browser support.

| Minor | First stable / compiler result | Latest stable / compiler result |
| --- | --- | --- |
| 1.0 | 1.0.0: build-failed | 1.0.5: build-failed |
| 1.1 | 1.1.0: build-failed | 1.1.1: build-failed |
| 1.2 | 1.2.0: build-failed | 1.2.6: build-failed |
| 1.3 | 1.3.0: build-failed | 1.3.4: build-failed |
| 1.4 | 1.4.0: build-failed | 1.4.5: build-failed |
| 1.5 | 1.5.0: build-failed | 1.5.3: build-failed |
| 1.6 | 1.6.0: build-failed | 1.6.6: build-failed |
| 1.7 | 1.7.0: build-failed | 1.7.4: build-failed |
| 1.8 | 1.8.0: build-failed | 1.8.2: build-failed |
| 1.9 | 1.9.0: build-failed | 1.9.4: build-failed |
| 1.10 | 1.10.0: build-failed | 1.10.4: build-failed |
| 1.11 | 1.11.0: build-failed | 1.11.4: build-failed |
| 1.12 | 1.12.0: build-failed | 1.12.3: build-failed |
| 1.13 | 1.13.0: build-failed | 1.13.4: build-failed |
| 1.14 | 1.14.0: build-failed | 1.14.5: build-failed |
| 1.15 | 1.15.0: build-failed | 1.15.8: build-failed |
| 1.16 | 1.16.0: build-failed | 1.16.3: build-failed |
| 1.17 | 1.17.0: build-failed | 1.17.3: build-failed |
| 1.18 | 1.18.0: build-failed | 1.18.5: built |
| 1.19 | 1.19.0: built | 1.19.6: built |
| 1.20 | 1.20.0: built | 1.20.4: built |

See the [compiler evidence](../evidence/compiler-otp29.json) for exact diagnostics and log hashes. Browser validation is recorded separately. The historic compiler recipe under `families/historical/` is a separate attempt with an era-appropriate OTP toolchain; it does not change the results of the OTP 29 experiment.
