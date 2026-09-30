"""Adapt the pinned Unix platform to a single-scheduler WASI command."""
from pathlib import Path
import shutil

root = Path('/src/atomvm')
recipe = Path('/builder/wasi')
platform = root / 'src/platforms/generic_unix'
shutil.copyfile(recipe / 'CMakeLists.txt', root / 'CMakeLists.txt')
shutil.copyfile(recipe / 'mapped_file.c', platform / 'lib/mapped_file.c')

def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError('Upstream patch context changed: ' + str(path))
    path.write_text(text.replace(old, new))

sys = platform / 'lib/sys.c'
for header in ['otp_net.h', 'otp_socket.h']:
    replace(sys, '#include "' + header + '"\n', '')
replace(sys, 'return socket_init(glb, opts);', 'return NULL;')
replace(sys, '    otp_net_init(global);\n    otp_socket_init(global);', '')
replace(sys, '#include <signal.h>\n', '')
nifs = platform / 'lib/platform_nifs.c'
text = nifs.read_text()
start = text.index('    const struct Nif *nif = otp_net_nif_get_nif(nifname);')
text = text[:start] + '    return NULL;\n}\n'
nifs.write_text(text)
for header in ['otp_net.h', 'otp_socket.h']:
    replace(nifs, '#include "' + header + '"\n', '')
replace(platform / 'lib/platform_defaultatoms.c', '"\\xC" "generic_unix"', '"\\x4" "wasi"')
replace(platform / 'main.c', '            if (!iff_is_valid_beam(mapped_file->mapped)) {', '            if (!mapped_file || !iff_is_valid_beam(mapped_file->mapped)) {')
core_nifs = root / 'src/libAtomVM/nifs.c'
text = core_nifs.read_text()
start = text.index('\nterm nif_erlang_localtime(Context *ctx, int argc, term argv[])\n{') + 1
end = text.index('term nif_erlang_timestamp_0(', start)
text = text[:start] + '''term nif_erlang_localtime(Context *ctx, int argc, term argv[])
{
    if (argc != 0) {
        RAISE_ERROR(BADARG_ATOM);
    }
    struct timespec ts;
    struct tm storage;
    sys_time(&ts);
    return build_datetime_from_tm(ctx, gmtime_r(&ts.tv_sec, &storage));
}

''' + text[end:]
core_nifs.write_text(text)
