FROM python:3.8-alpine as base
FROM base as builder
RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apk add python3-dev alpine-sdk
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app

CMD ["uvicorn", "--port=8083","--workers=1", "ta:app"]
EXPOSE 8082
