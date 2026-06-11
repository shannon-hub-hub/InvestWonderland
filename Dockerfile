FROM python:3.11-slim-bookworm

ARG TARGETARCH
RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium chromium-driver curl ca-certificates \
    && case "${TARGETARCH}" in \
        arm64)  SUPERCRONIC_ARCH=linux-arm64 ;; \
        *)      SUPERCRONIC_ARCH=linux-amd64 ;; \
       esac \
    && curl -fsSLo /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-${SUPERCRONIC_ARCH}" \
    && chmod +x /usr/local/bin/supercronic \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    HEADLESS=true

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY app ./app
COPY db ./db
COPY scripts ./scripts
COPY invest_scraper.py companies_scraper.py ./
COPY crontab ./crontab

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir . \
    && chmod +x scripts/cron/*.sh

EXPOSE 8000
