# vanishd

[![CI](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml)
[![Release](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=NatanRigailo_vanishd&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=NatanRigailo_vanishd)
[![GitHub release](https://img.shields.io/github/v/release/NatanRigailo/vanishd)](https://github.com/NatanRigailo/vanishd/releases)

Zero-knowledge secret sharing with one-time links — the server never sees the plaintext.

## How it works

1. Sender types the secret in the browser
2. The browser encrypts it locally (AES-256-GCM) and sends only the ciphertext to the server
3. A one-time link is generated — the decryption key lives in the URL `#fragment`, invisible to the server
4. Recipient opens the link — the browser decrypts locally and displays the content
5. The server deletes the record on first read — the link never works twice

There is also a password mode: the sender defines a password that the recipient must type (PBKDF2 derives the AES key in the browser).

## Quick start

```bash
docker run -d \
  -p 8080:8080 \
  -v vanishd_data:/data \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  ghcr.io/natanrigailo/vanishd:latest
```

Open `http://localhost:8080`.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | generated at runtime | Flask secret key — set explicitly in production |
| `LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEFAULT_LANGUAGE` | `pt-BR` | UI default language (`pt-BR` or `en`) |
| `MAX_TTL_SECONDS` | `604800` | Maximum allowed TTL (7 days) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Requests per minute per IP on the read endpoint |
| `RATE_LIMIT_POST_PER_MINUTE` | `10` | Requests per minute per IP on the write endpoint |
| `MAX_CONTENT_LENGTH` | `65536` | Maximum request body size (bytes) |
| `CLEANUP_INTERVAL_SECONDS` | `3600` | Interval for the expired secrets cleanup job |
| `DATABASE_PATH` | `/data/vanishd.db` | SQLite file path |

## Local development

```bash
git clone https://github.com/NatanRigailo/vanishd.git
cd vanishd
cp .env.example .env
make up       # build + start on port 8080
make logs     # follow logs
make down     # stop
```

## Roadmap

### v0.1 — Foundation ✅
- [x] Project structure, multi-stage non-root Dockerfile
- [x] Flask app skeleton with `/healthz` and structured logging
- [x] SQLite schema

### v0.2 — Core Feature ✅
- [x] Client-side AES-256-GCM via Web Crypto API
- [x] `POST /api/secrets` and `GET /api/secrets/:id` with atomic delete
- [x] Link mode (key in `#fragment`) and password mode (PBKDF2)
- [x] Minimal create and view UI

### v0.3 — CI Pipeline ✅
- [x] Lint (flake8 + hadolint), SAST (bandit), Build + Trivy scan
- [x] SonarCloud quality gate
- [x] Dependabot (pip, Docker, Actions)

### v0.4 — Security Hardening ✅
- [x] Per-IP rate limiting on the read endpoint
- [x] Secure HTTP headers + CSP without `unsafe-inline`
- [x] Cleanup job for expired secrets
- [x] Access logging without exposing sensitive content

### v0.5 — Release & Deploy ✅
- [x] Semver auto-tagging via Conventional Commits
- [x] Automatic publish to GHCR
- [x] Automatic deploy to Render via deploy hook
- [x] README with badges, quick start, and roadmap

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
