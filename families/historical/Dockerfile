# syntax=docker/dockerfile:1.7
ARG COMPILER_IMAGE=erlang:17.5@sha256:3e75172790a9fcfdcc32f8c94297e6134b59a48bb86091f08172e4d5b2a6ae44
FROM ${COMPILER_IMAGE} AS compiled
ARG ELIXIR_VERSION=1.0.0
ARG ELIXIR_SHA256
ARG JOBS=2
ENV LANG=C.UTF-8 ERL_FLAGS="+S 2:2"
WORKDIR /src/elixir
COPY sources/elixir-${ELIXIR_VERSION}.tar.gz /tmp/elixir.tar.gz
COPY families/historical/stdio.patch /builder/stdio.patch
RUN test -n "${ELIXIR_SHA256}" \
    && echo "${ELIXIR_SHA256}  /tmp/elixir.tar.gz" | sha256sum -c - \
    && tar -xf /tmp/elixir.tar.gz --strip-components=1 \
    && if grep -Fq "ok = io:setopts(standard_error, [{unicode,true}])" lib/elixir/src/elixir.erl; then patch -p1 < /builder/stdio.patch; fi \
    && if grep -Fq '../../$(REBAR)' Makefile; then make -j${JOBS} REBAR="rebar -j1"; else make -j${JOBS} REBAR="/src/elixir/rebar -j1"; fi \
    && mkdir -p /out \
    && bin/elixir -e 'IO.puts(System.version()); IO.inspect(6 * 7)' > /out/native-smoke.txt
COPY families/historical/export_forms.erl /builder/
RUN erlc -o /builder /builder/export_forms.erl \
    && erl -noshell -pa /builder lib/*/ebin -s export_forms run
FROM scratch AS artifacts
COPY --from=compiled /src/elixir/lib/ /lib/
COPY --from=compiled /src/elixir/LICENSE /ELIXIR-LICENSE
COPY --from=compiled /out/native-smoke.txt /native-smoke.txt
