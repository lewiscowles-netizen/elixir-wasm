# syntax=docker/dockerfile:1.7
ARG JS_IMAGE
FROM ${JS_IMAGE} AS sdk
ARG POPCORN_SHA256
COPY sources/popcorn.tar.gz /tmp/popcorn.tar.gz
RUN echo "${POPCORN_SHA256}  /tmp/popcorn.tar.gz" | sha256sum -c - && mkdir -p /src/popcorn \
    && tar -xf /tmp/popcorn.tar.gz --strip-components=1 -C /src/popcorn
WORKDIR /builder/js
COPY families/popcorn/js/package.json families/popcorn/js/yarn.lock ./
RUN yarn install --frozen-lockfile --non-interactive
COPY families/popcorn/js/bundle.cjs ./
RUN node bundle.cjs
FROM otp-base AS packaged
COPY --from=sdk /sdk/ /sdk/
COPY families/popcorn/package.exs families/popcorn/package.py families/popcorn/popcorn_lab.ex families/popcorn/Dockerfile /builder/recipe/
COPY families/popcorn/js/package.json families/popcorn/js/yarn.lock families/popcorn/js/bundle.cjs /builder/recipe/js/
COPY families/backends.lock.json /builder/
RUN /src/tools/bin/elixir /builder/recipe/package.exs && python3 /builder/recipe/package.py && python3 /builder/record-provenance.py
FROM scratch AS artifacts
COPY --from=packaged /artifacts/ /
