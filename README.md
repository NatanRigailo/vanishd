# vanishd

[![CI](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml)
[![Release](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=NatanRigailo_vanishd&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=NatanRigailo_vanishd)
[![GitHub release](https://img.shields.io/github/v/release/NatanRigailo/vanishd)](https://github.com/NatanRigailo/vanishd/releases)

Zero-knowledge secret sharing with one-time links — the server never sees the plaintext.

## Screenshot

![vanishd create page](docs/screenshots/create.png)

## How it works

The browser encrypts the secret locally and sends only the ciphertext to the server. The decryption key never leaves the client.

```
[Sender browser]                       [Server]              [Recipient browser]
   generates AES-256-GCM key
   encrypts the secret (AES-GCM)
   POST /api/secrets {ciphertext} ──► stores encrypted blob
   receives {id}                       never saw the plaintext
   builds URL: /s/{id}#{base64(key)}
                                                              opens the link
                                                              extracts key from #fragment
                                                              GET /api/secrets/{id} ──► returns + deletes
                                                              decrypts locally with the key
                                                              displays the secret
                                                              (link invalid forever)
```

**Password mode (PBKDF2):** the sender sets a password; the browser derives the AES key via PBKDF2 (200k iterations, SHA-256). The link does not carry the key — the recipient types the password to decrypt. The server stores `ciphertext + salt`, never the key or plaintext.

## Security model

| What the server stores | What the server never sees |
|---|---|
| Encrypted ciphertext (AES-256-GCM) | The plaintext secret |
| Random salt (password mode) | The AES key |
| Secret ID and TTL | The `#fragment` of the URL |
| Per-IP request counters | The password |

**Guarantees this design provides:**

- A server breach exposes only ciphertext — useless without the key
- The one-time delete ensures the link stops working after the first read
- The URL fragment (`#key`) is never sent to the server by browsers
- In password mode, the key is derived entirely in the browser — the server cannot brute-force it without the ciphertext *and* the password

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
| `DATABASE_URL` | *(unset)* | PostgreSQL connection string — overrides `DATABASE_PATH` when set |

## Local development

```bash
git clone https://github.com/NatanRigailo/vanishd.git
cd vanishd
cp .env.example .env
make up       # build + start on port 8080
make logs     # follow logs
make down     # stop
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
