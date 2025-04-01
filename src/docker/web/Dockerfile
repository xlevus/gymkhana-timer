FROM python:3.12-slim AS static

ENV STATIC_ROOT=/data/static

COPY src.python.gk.web/manage.pex /manage.pex
RUN mkdir -p $STATIC_ROOT && /manage.pex collectstatic --no-input

FROM python:3.12-slim

EXPOSE 8080

COPY src/docker/web/entrypoint.sh /entrypoint.sh
COPY --from=static /data /data
COPY src.python.gk.web/*.pex /

ENTRYPOINT /entrypoint.sh