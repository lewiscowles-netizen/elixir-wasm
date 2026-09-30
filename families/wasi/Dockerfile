# syntax=docker/dockerfile:1.7
ARG BUILD_IMAGE
FROM ${BUILD_IMAGE} AS wasm
ARG SDK_FILE
ARG SDK_SHA256
ARG ATOMVM_SHA256
RUN apt-get update && apt-get install -y --no-install-recommends cmake gperf python3 && rm -rf /var/lib/apt/lists/*
COPY sources/${SDK_FILE} /tmp/wasi-sdk.tar.gz
COPY sources/atomvm-0.6.6.tar.gz /tmp/atomvm.tar.gz
RUN echo "${SDK_SHA256}  /tmp/wasi-sdk.tar.gz" | sha256sum -c - && echo "${ATOMVM_SHA256}  /tmp/atomvm.tar.gz" | sha256sum -c - \
    && mkdir -p /opt/wasi-sdk /src/atomvm \
    && tar -xf /tmp/wasi-sdk.tar.gz --strip-components=1 -C /opt/wasi-sdk \
    && tar -xf /tmp/atomvm.tar.gz --strip-components=1 -C /src/atomvm
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
COPY families/wasi/CMakeLists.txt families/wasi/mapped_file.c families/wasi/prepare.py /builder/wasi/
RUN python3 /builder/wasi/prepare.py \
    && cmake -S /src/atomvm -B /src/atomvm/wasi -DCMAKE_TOOLCHAIN_FILE=/opt/wasi-sdk/share/cmake/wasi-sdk-p1.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE="-Os -DNDEBUG" \
    && cmake --build /src/atomvm/wasi --target AtomVM -j4
FROM compiler-base AS probes
COPY families/wasi/compile-probes.exs /builder/compile-probes.exs
COPY examples/wasi/hello.exs /builder/probe.exs
RUN elixir /builder/compile-probes.exs
FROM wasm AS packaged
ARG ELIXIR_VERSION
COPY --from=compiler-base /program/ /program/
COPY --from=compiler-base /src/atomvm/build/libs/atomvmlib.avm /program/atomvmlib.avm
COPY --from=compiler-base /src/elixir/LICENSE /program/ELIXIR-LICENSE
COPY --from=probes /probes/ /probes/
COPY families/backends.lock.json sources.lock.json versions.json /builder/
COPY families/atomvm/ /builder/atomvm/
COPY families/wasi/ /builder/wasi/
COPY scripts/package-wasi.py /builder/package-wasi.py
RUN python3 /builder/package-wasi.py ${ELIXIR_VERSION} ${SDK_FILE}
FROM scratch AS artifacts
COPY --from=packaged /artifacts/ /
