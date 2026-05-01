FROM python:3.14-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.14-slim

RUN groupadd -r vanishd \
 && useradd -r -g vanishd -d /app -s /sbin/nologin vanishd

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY wsgi.py .

RUN mkdir /data && chown vanishd:vanishd /data

USER vanishd

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "wsgi:app"]
