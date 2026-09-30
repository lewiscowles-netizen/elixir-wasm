# syntax=docker/dockerfile:1.7
ARG COMPILER_IMAGE
ARG EMSDK_IMAGE
FROM ${COMPILER_IMAGE} AS compiler
ARG ELIXIR_VERSION
ARG ELIXIR_SHA256
ARG ATOMVM_SHA256
ENV ERL_FLAGS="+S 2:2" LC_ALL=C.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends cmake gcc g++ make gperf zlib1g-dev python3 && rm -rf /var/lib/apt/lists/*
COPY sources/atomvm-0.6.6.tar.gz /tmp/atomvm.tar.gz
COPY sources/elixir-${ELIXIR_VERSION}.tar.gz /tmp/elixir.tar.gz
RUN echo "${ATOMVM_SHA256}  /tmp/atomvm.tar.gz" | sha256sum -c - && echo "${ELIXIR_SHA256}  /tmp/elixir.tar.gz" | sha256sum -c - \
    && mkdir -p /src/atomvm /src/elixir && tar -xf /tmp/atomvm.tar.gz --strip-components=1 -C /src/atomvm \
    && tar -xf /tmp/elixir.tar.gz --strip-components=1 -C /src/elixir && cd /src/elixir && make -j2
ENV PATH="/src/elixir/bin:${PATH}"
RUN cmake -S /src/atomvm -B /src/atomvm/build -DAVM_BUILD_RUNTIME_ONLY=ON -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /src/atomvm/build --target AtomVM atomvmlib -j4
COPY --from=program-source /source.exs /program/source.exs
COPY families/atomvm/compile.exs /builder/compile.exs
RUN elixir /builder/compile.exs \
    && /src/atomvm/build/tools/packbeam/PackBEAM /program/program.avm /program/Elixir.AtomVMLab.beam \
    && /src/atomvm/build/src/AtomVM /program/program.avm /src/atomvm/build/libs/atomvmlib.avm > /program/native-smoke.txt
FROM ${EMSDK_IMAGE} AS wasm
ARG ATOMVM_SHA256
RUN apt-get update && apt-get install -y --no-install-recommends gperf && rm -rf /var/lib/apt/lists/*
COPY sources/atomvm-0.6.6.tar.gz /tmp/atomvm.tar.gz
RUN echo "${ATOMVM_SHA256}  /tmp/atomvm.tar.gz" | sha256sum -c - && mkdir -p /src/atomvm \
    && tar -xf /tmp/atomvm.tar.gz --strip-components=1 -C /src/atomvm
COPY families/atomvm/prepare.py /builder/prepare.py
RUN python3 /builder/prepare.py \
    && emcmake cmake -S /src/atomvm/src/platforms/emscripten -B /src/atomvm/wasm -DAVM_EMSCRIPTEN_ENV=web -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /src/atomvm/wasm --target AtomVM -j4
FROM wasm AS packaged
ARG ELIXIR_VERSION
COPY --from=compiler /program/ /program/
COPY --from=compiler /src/atomvm/build/libs/atomvmlib.avm /program/atomvmlib.avm
COPY --from=compiler /src/elixir/LICENSE /program/ELIXIR-LICENSE
COPY families/backends.lock.json sources.lock.json versions.json /builder/
COPY families/atomvm/ /builder/recipe/
COPY scripts/package-backend.py /builder/package-backend.py
RUN python3 /builder/package-backend.py atomvm ${ELIXIR_VERSION}
FROM scratch AS artifacts
COPY --from=packaged /artifacts/ /
