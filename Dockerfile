FROM python:3.13-slim-bookworm as build-image

RUN apt-get update
RUN apt-get install -y curl ca-certificates gnupg
RUN curl -fSsL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /usr/share/keyrings/postgresql.gpg > /dev/null
RUN apt-get update

RUN apt-get install -y gcc g++ make postgresql-server-dev-all libpq-dev libffi-dev git cargo

COPY ./ /tmp/build

RUN  (cd /tmp/build \
     && python3 -m venv venv-dev \
     && . venv-dev/bin/activate \
     && python3 -m pip install -U -r requirements_dev.txt \
     && python3 setup.py bdist_wheel)

WORKDIR /usr/local/app

COPY src/dataset_image_annotator/db/migrations ./migrations/
COPY src/dataset_image_annotator/db/alembic.ini ./alembic.ini

RUN  (python3 -m venv venv \
      && . venv/bin/activate \
      && python3 -m pip install -U pip \
      && python3 -m pip install -U setuptools \
      && python3 -m pip install -U wheel \
      && python3 -m pip install -U uvloop \
      && python3 -m pip install -U /tmp/build/dist/*.whl)


FROM python:3.13-slim-bookworm

ENV  PYTHONPATH=/usr/local/app

COPY --from=build-image /usr/share/keyrings/ /usr/share/keyrings/
RUN  mkdir -p /usr/local/app \
     && apt-get update \
     && apt-get install -y libpq-dev

WORKDIR /usr/local/app

COPY --from=build-image /usr/local/app/ ./

RUN  groupadd -r appgroup \
     && useradd -r -G appgroup -d /home/appuser appuser \
     && install -d -o appuser -g appgroup /usr/local/app/logs

USER  appuser

EXPOSE 8080


CMD ["/usr/local/app/venv/bin/python3", "-m", "uvicorn", "dataset_image_annotator.api.http:app", \
     "--host", "0.0.0.0", "--port", "8080"]
