const esbuild = require('esbuild');
const options = { bundle: true, format: 'esm', platform: 'browser', target: 'es2022', legalComments: 'linked' };
async function main() {
  await esbuild.build({ ...options, entryPoints: ['/src/popcorn/popcorn/js/src/index.ts'], outfile: '/sdk/popcorn.mjs' });
  await esbuild.build({ ...options, entryPoints: ['/src/popcorn/popcorn/js/src/worker.ts'], outfile: '/sdk/popcorn-worker.mjs', plugins: [{ name: 'runtime-loader', setup(build) { build.onResolve({ filter: /assets\/beam\.mjs$/ }, () => ({ path: './beam.mjs', external: true })); } }] });
}
main().catch(error => { console.error(error); process.exitCode = 1; });
