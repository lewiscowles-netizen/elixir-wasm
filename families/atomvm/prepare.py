from pathlib import Path

path = Path('/src/atomvm/src/platforms/emscripten/src/CMakeLists.txt')
source = path.read_text()
old = '-sEXPORTED_RUNTIME_METHODS=ccall '
assert source.count(old) == 1
source = source.replace(old, '-sEXPORTED_RUNTIME_METHODS=ccall,FS_createDataFile,FS_mkdirTree -sMODULARIZE=1 -sEXPORT_ES6=1 -sEXPORT_NAME=createAtomVM -sEXIT_RUNTIME=1 -sALLOW_MEMORY_GROWTH=1 ')
source += '\nset_target_properties(AtomVM PROPERTIES SUFFIX ".mjs")\n'
path.write_text(source)
