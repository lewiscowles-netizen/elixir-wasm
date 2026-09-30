cmake_minimum_required(VERSION 3.20)
project(AtomVMWASI C)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/CMakeModules)
set(AVM_DISABLE_SMP ON)
set(AVM_DISABLE_TASK_DRIVER ON)
set(AVM_RELEASE ON)
set(AVM_CREATE_STACKTRACES ON)
add_subdirectory(src/libAtomVM)
set(PLATFORM src/platforms/generic_unix)
add_library(libAtomVM${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}
    ${PLATFORM}/lib/sys.c
    ${PLATFORM}/lib/mapped_file.c
    ${PLATFORM}/lib/platform_defaultatoms.c
    ${PLATFORM}/lib/platform_nifs.c)
target_include_directories(libAtomVM${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR} PUBLIC ${PLATFORM}/lib)
target_link_libraries(libAtomVM${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR} PUBLIC libAtomVM)
add_executable(AtomVM ${PLATFORM}/main.c)
target_link_libraries(AtomVM PRIVATE libAtomVM)
target_link_options(AtomVM PRIVATE -Wl,-z,stack-size=1048576 -Wl,--max-memory=268435456)
set_target_properties(AtomVM PROPERTIES SUFFIX .wasm)
