# syntax=docker/dockerfile:1.7
ARG OTP_IMAGE=hexpm/erlang:29.0.6-ubuntu-noble-20260911@sha256:7bc4f2c3eea8acec1d27572f85c22c55c50d7def5b9790ea7c94c7ff93cf6e78
ARG EMSDK_IMAGE=emscripten/emsdk:6.0.2@sha256:644883f58ca15c38c8be59b3a727ba0eff347729bc31d50a3348a6c9ed92bc07
FROM ${OTP_IMAGE} AS native-otp
FROM ${EMSDK_IMAGE} AS toolchain
ENV LC_ALL=C.UTF-8 TZ=UTC ERL_FLAGS="+S 2:2" SOURCE_DATE_EPOCH=1790640000
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git make gcc g++ autoconf automake libtool \
    libssl-dev libncurses-dev default-jre-headless xz-utils \
    && rm -rf /var/lib/apt/lists/*
COPY --from=native-otp /usr/local/ /usr/local/
COPY sources.lock.json versions.json /builder/
COPY scripts/verify-source.py /builder/
COPY sources/autoconf.tar.gz /sources/autoconf.tar.gz
RUN python3 /builder/verify-source.py autoconf.tar.gz \
    && mkdir -p /src && tar -xf /sources/autoconf.tar.gz -C /src \
    && cd /src/autoconf-2.72 && ./configure --prefix=/usr/local \
    && make -j4 && make install
FROM toolchain AS runtime
ARG JOBS=4
COPY sources/otp.tar.gz sources/popcorn.tar.gz /sources/
RUN python3 /builder/verify-source.py otp.tar.gz popcorn.tar.gz \
    && mkdir -p /src/popcorn /src/otp \
    && tar -xf /sources/popcorn.tar.gz --strip-components=1 -C /src/popcorn \
    && tar -xf /sources/otp.tar.gz --strip-components=1 -C /src/otp \
    && cd /src/otp && git init -q && git add . \
    && git -c user.name=Builder -c user.email=builder@localhost commit -qm 'Pinned OTP source archive'
WORKDIR /src/popcorn
RUN apt-get update && apt-get install -y --no-install-recommends libsctp1 && rm -rf /var/lib/apt/lists/*
COPY scripts/runtime-phase.sh /builder/runtime-phase.sh
RUN JOBS=${JOBS} bash /builder/runtime-phase.sh prepare
RUN bash /builder/runtime-phase.sh configure
RUN JOBS=${JOBS} bash /builder/runtime-phase.sh compile
RUN bash /builder/runtime-phase.sh export
FROM scratch AS runtime-artifacts
COPY --from=runtime /out/ /
FROM toolchain AS elixir
ARG ELIXIR_VERSION=1.20.4
ARG JOBS=4
COPY sources/elixir-${ELIXIR_VERSION}.tar.gz /sources/
RUN python3 /builder/verify-source.py elixir-${ELIXIR_VERSION}.tar.gz \
    && mkdir -p /src/elixir && tar -xf /sources/elixir-${ELIXIR_VERSION}.tar.gz --strip-components=1 -C /src/elixir
WORKDIR /src/elixir
RUN make -j${JOBS}
FROM scratch AS elixir-artifacts
COPY --from=elixir /src/elixir/lib/ /lib/
COPY --from=elixir /src/elixir/LICENSE /ELIXIR-LICENSE
FROM toolchain AS packaging-tools
COPY sources/elixir-1.20.4.tar.gz /sources/
RUN python3 /builder/verify-source.py elixir-1.20.4.tar.gz \
    && mkdir -p /src/tools && tar -xf /sources/elixir-1.20.4.tar.gz --strip-components=1 -C /src/tools \
    && cd /src/tools && make -j4
FROM runtime AS packaged
ARG ELIXIR_VERSION=1.20.4
COPY --from=packaging-tools /src/tools /src/tools
COPY --from=elixir /src/elixir/lib /src/selected-elixir/lib
COPY --from=elixir /src/elixir/LICENSE /src/selected-elixir/LICENSE
COPY sources/elixir-${ELIXIR_VERSION}.tar.gz /selected-source.tar.gz
COPY scripts/package.exs scripts/lab_runner.erl scripts/artifacts.py scripts/notices.py /builder/
RUN /src/tools/bin/elixir /builder/package.exs && python3 /builder/artifacts.py ${ELIXIR_VERSION}
COPY Dockerfile /builder/recipe/Dockerfile
COPY families/historical/ /builder/recipe/historical/
COPY scripts/record-provenance.py /builder/
RUN python3 /builder/record-provenance.py
FROM scratch AS browser-artifacts
COPY --from=packaged /artifacts/ /
FROM elixir AS project
COPY --from=project-source / /project/
WORKDIR /project
ENV MIX_ENV=prod
RUN export PATH=/src/elixir/bin:$PATH && mix deps.compile && mix compile --no-deps-check \
    && cp -aL _build/prod/lib /project-bundle
FROM packaged AS project-packaged
ARG APP_NAME
COPY --from=project /project-bundle/ /project/_build/prod/lib/
COPY scripts/package-project.py /builder/
RUN python3 /builder/package-project.py ${APP_NAME} && python3 /builder/artifacts.py ${ELIXIR_VERSION} && python3 /builder/record-provenance.py
FROM scratch AS project-artifacts
COPY --from=project-packaged /artifacts/ /
FROM runtime AS historical-packaged
ARG ELIXIR_VERSION=1.0.0
ARG HISTORICAL_OTP=17.5
ARG HISTORICAL_IMAGE=erlang:17.5@sha256:3e75172790a9fcfdcc32f8c94297e6134b59a48bb86091f08172e4d5b2a6ae44
ENV HISTORICAL_OTP=${HISTORICAL_OTP} HISTORICAL_IMAGE=${HISTORICAL_IMAGE}
COPY --from=packaging-tools /src/tools /src/tools
COPY --from=historical-input /lib/ /src/selected-elixir/lib/
COPY --from=historical-input /ELIXIR-LICENSE /src/selected-elixir/LICENSE
COPY sources/elixir-${ELIXIR_VERSION}.tar.gz /selected-source.tar.gz
COPY scripts/package.exs scripts/lab_runner.erl scripts/artifacts.py scripts/notices.py scripts/recompile-historical.exs scripts/elixir_wasm_compat.erl /builder/
RUN /src/tools/bin/elixir /builder/recompile-historical.exs \
    && /src/tools/bin/elixir /builder/package.exs \
    && python3 /builder/artifacts.py ${ELIXIR_VERSION}
COPY Dockerfile /builder/recipe/Dockerfile
COPY families/historical/ /builder/recipe/historical/
COPY scripts/record-provenance.py /builder/
RUN python3 /builder/record-provenance.py
FROM scratch AS historical-browser-artifacts
COPY --from=historical-packaged /artifacts/ /
