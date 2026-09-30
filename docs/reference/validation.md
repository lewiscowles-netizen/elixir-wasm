# Measured compatibility

Each column records a different operation. Historical entries execute retargeted Elixir on OTP 29, subject to the [family limitations](historical-families.md). A browser pass covers the [acceptance probes](../how-to/test.md), not every API. A successful browser build also establishes that its required native compiler stage passed; earlier standalone failures remain in the evidence.

| Elixir | Native compiler stage | Browser bundle | Chromium execution |
| --- | --- | --- | --- |
| 1.0.0 | passed | built | passed |
| 1.0.5 | passed | built | passed |
| 1.1.0 | passed | built | passed |
| 1.1.1 | passed | built | passed |
| 1.2.0 | passed | built | passed |
| 1.2.6 | passed | built | passed |
| 1.3.0 | passed | built | passed |
| 1.3.4 | passed | built | passed |
| 1.4.0 | passed | built | passed |
| 1.4.5 | passed | built | passed |
| 1.5.0 | passed | built | passed |
| 1.5.3 | passed | built | passed |
| 1.6.0 | passed | built | passed |
| 1.6.6 | passed | built | passed |
| 1.7.0 | passed | built | passed |
| 1.7.4 | passed | built | passed |
| 1.8.0 | passed | built | passed |
| 1.8.2 | passed | built | passed |
| 1.9.0 | passed | built | passed |
| 1.9.4 | passed | built | passed |
| 1.10.0 | passed | built | passed |
| 1.10.4 | passed | built | passed |
| 1.11.0 | passed | built | passed |
| 1.11.4 | passed | built | passed |
| 1.12.0 | passed | built | passed |
| 1.12.3 | passed | built | passed |
| 1.13.0 | passed | built | passed |
| 1.13.4 | passed | built | passed |
| 1.14.0 | passed | built | passed |
| 1.14.5 | passed | built | passed |
| 1.15.0 | passed | built | passed |
| 1.15.8 | passed | built | passed |
| 1.16.0 | passed | built | passed |
| 1.16.3 | passed | built | passed |
| 1.17.0 | passed | built | passed |
| 1.17.3 | passed | built | passed |
| 1.18.0 | passed | built | passed |
| 1.18.5 | passed | built | passed |
| 1.19.0 | passed | built | passed |
| 1.19.6 | passed | built | passed |
| 1.20.0 | passed | built | passed |
| 1.20.4 | passed | built | passed |

The [machine-readable evidence](../evidence/validation.json) includes source and manifest hashes. The [separate OTP 29 compiler experiment](../evidence/compiler-otp29.json) deliberately includes unsupported native combinations; it is not the historical family recipe. WASI results are recorded separately in the [WASI reference](wasi.md).
