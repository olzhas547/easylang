FROM python:3.11.0

WORKDIR /easylang

COPY ./requirements.txt /easylang/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /easylang/requirements.txt

COPY ./app /easylang/app
COPY ./.env /easylang/.env

ENV PYTHONPATH "${PYTHONPATH}:/easylang/app"

#CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]
