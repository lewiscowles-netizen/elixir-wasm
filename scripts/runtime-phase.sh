#!/usr/bin/env bash
set -euo pipefail
cd /src/popcorn
python3 - <<'PY'
from pathlib import Path
source = Path('scripts/build-beam.sh').read_text()
assert source.rstrip().endswith('main "$@"')
source = source[:source.rfind('main "$@"')]
old = 'git -C "${beam_dir}" add "${files[@]}"'
assert source.count(old) == 1
source = source.replace(old, 'git -C "${beam_dir}" add -f "${files[@]}"')
Path('scripts/build-beam-functions.sh').write_text(source)
PY
source scripts/build-beam-functions.sh
beam_dir=/src/popcorn/popcorn/sources/otp
case "$1" in
  prepare)
    mkdir -p popcorn/sources
    setup_otp_source /src/otp OTP-29.0.6
    patch_otp
    run_autoconf "$beam_dir"
    compile_preloaded_modules "$beam_dir" true true
    build_bootstrap "$beam_dir" "${JOBS:-4}"
    ;;
  configure)
    compile_preloaded_modules "$beam_dir" true true
    commit_preloaded_modules "$beam_dir"
    run_configure "$beam_dir" release false ""
    ;;
  compile)
    build_beam "$beam_dir" release "${JOBS:-4}"
    ;;
  export)
    scripts/runtime-manifest.sh --beam-dir "$beam_dir" --outdir /out --with-crypto false
    copy_artifacts "$beam_dir" /out false
    ;;
  *) exit 2 ;;
esac
