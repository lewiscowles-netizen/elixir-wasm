# Documentation index

Each document has one purpose. The learning path grows from running a script to compiling a module and bundling a project.

| Type | Document | Use it for |
| --- | --- | --- |
| Tutorial | [Your first browser script](tutorials/01-script.md) | Run Elixir and inspect its actual version |
| Tutorial | [Modules, processes and state](tutorials/02-modules.md) | Grow a script into collaborating modules |
| Tutorial | [Bundle a Mix project](tutorials/03-project.md) | Package a project and a local dependency |
| Tutorial | [Evaluate through Popcorn](tutorials/04-popcorn.md) | Call JavaScript from Elixir through the SDK bridge |
| Tutorial | [Run a compiled AtomVM script](tutorials/05-atomvm.md) | Compile a program and run it on stock AtomVM |
| Tutorial | [Run an Elixir WASI command](tutorials/06-wasi.md) | Compile and run outside the browser, then grant a data directory |
| How-to | [Build and verify WASI](how-to/wasi.md) | Package a script and record host execution evidence |
| Reference | [WASI command](reference/wasi.md) | Check the ABI, versions, capabilities and artifacts |
| Explanation | [The separate WASI port](explanation/wasi.md) | Understand scheduling and filesystem capabilities |
| How-to | [Build Popcorn](how-to/popcorn.md) | Package the upstream SDK and supervised evaluator |
| How-to | [Build AtomVM](how-to/atomvm.md) | Compile and import a precompiled script |
| How-to | [Build selected versions](how-to/build.md) | Reproduce exact release builds |
| How-to | [Closed networks](how-to/offline.md) | Prepare assets and diagnose missing egress |
| How-to | [Debug failures](how-to/debug.md) | Separate build, boot and application failures |
| How-to | [Verify browser execution](how-to/test.md) | Run acceptance tests and inspect evidence |
| How-to | [Package a portable lab](how-to/package-lab.md) | Render documentation and export a standalone archive |
| Reference | [Measured compatibility](reference/validation.md) | Compare native builds, bundles and actual browser passes |
| Reference | [Runtime integrations](reference/backends.md) | Compare distinct backend contracts and evidence |
| Reference | [Popcorn integration](reference/popcorn.md) | Check the SDK version, APIs and supported compiler line |
| Reference | [AtomVM integration](reference/atomvm.md) | Check precompilation, libraries and limitations |
| Reference | [Direct compilation on OTP 29](reference/versions.md) | Inspect the separate native compiler experiment |
| Reference | [Targets](reference/targets.md) | Check host contracts and unsupported features |
| Reference | [Artifacts](reference/artifacts.md) | Verify and deploy complete bundles |
| Reference | [Historical compiler families](reference/historical-families.md) | Inspect compiler selection and retargeting limitations |
| Explanation | [Architecture](explanation/architecture.md) | Understand what is compiled and what runs |
| Explanation | [Why use Popcorn?](explanation/popcorn.md) | Understand the browser and GenServer bridge |
| Explanation | [Why precompile for AtomVM?](explanation/atomvm.md) | Understand the smaller runtime's compilation boundary |
| Explanation | [What direct OTP means](explanation/direct-otp.md) | Separate application APIs from VM portability patches |
| Explanation | [Browser Wasm and WASI](explanation/targets.md) | Understand why different host APIs need different ports |
| Explanation | [Project compatibility](explanation/projects.md) | Assess a server application's browser boundary |

The [provenance appendix](reference/provenance.md) identifies the upstream work this builder uses.
