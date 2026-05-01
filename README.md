# vanishd

[![CI](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/ci.yml)
[![Release](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml/badge.svg)](https://github.com/NatanRigailo/vanishd/actions/workflows/release.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=NatanRigailo_vanishd&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=NatanRigailo_vanishd)
[![GitHub release](https://img.shields.io/github/v/release/NatanRigailo/vanishd)](https://github.com/NatanRigailo/vanishd/releases)

Compartilhamento de secrets zero-knowledge com links de uso único — o servidor nunca acessa o plaintext.

## Como funciona

1. Remetente digita o secret no navegador
2. O navegador cifra localmente (AES-256-GCM) e envia apenas o ciphertext ao servidor
3. Um link único é gerado — a chave de decifração fica no `#fragment` da URL, invisível ao servidor
4. Destinatário abre o link — o navegador decifra localmente e exibe o conteúdo
5. O servidor deleta o registro na primeira leitura — o link nunca funciona duas vezes

Existe também um modo senha: o remetente define uma senha que o destinatário precisa digitar (PBKDF2 deriva a chave AES no browser).

## Quick start

```bash
docker run -d \
  -p 8080:8080 \
  -v vanishd_data:/data \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  ghcr.io/natanrigailo/vanishd:latest
```

Acesse `http://localhost:8080`.

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | gerado em runtime | Chave Flask — defina explicitamente em produção |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_TTL_SECONDS` | `604800` | TTL máximo permitido (7 dias) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Requests por minuto por IP no endpoint de leitura |
| `CLEANUP_INTERVAL_SECONDS` | `3600` | Intervalo do job de limpeza de secrets expirados |
| `DATABASE_PATH` | `/data/vanishd.db` | Caminho do arquivo SQLite |

## Desenvolvimento local

```bash
git clone https://github.com/NatanRigailo/vanishd.git
cd vanishd
cp .env.example .env
make up       # build + sobe na porta 8080
make logs     # acompanhar logs
make down     # parar
```

## Roadmap

### v0.1 — Fundação ✅
- [x] Estrutura do projeto, Dockerfile multi-stage non-root
- [x] Flask app skeleton com `/healthz` e logging estruturado
- [x] SQLite schema

### v0.2 — Core Feature ✅
- [x] Client-side AES-256-GCM via Web Crypto API
- [x] `POST /api/secrets` e `GET /api/secrets/:id` com delete atômico
- [x] Modo link (chave no `#fragment`) e modo senha (PBKDF2)
- [x] UI mínima de criação e leitura

### v0.3 — CI Pipeline ✅
- [x] Lint (flake8 + hadolint), SAST (bandit), Build + Trivy scan
- [x] SonarCloud quality gate
- [x] Dependabot (pip, Docker, Actions)

### v0.4 — Security Hardening ✅
- [x] Rate limiting por IP no endpoint de leitura
- [x] Secure HTTP headers + CSP sem `unsafe-inline`
- [x] Cleanup job para secrets expirados
- [x] Logging de acessos sem expor conteúdo sensível

### v0.5 — Release & Deploy ✅
- [x] Auto-tag semver por Conventional Commits
- [x] Publish automático para GHCR
- [x] Deploy automático no Render via deploy hook
- [x] README com badges, quick start e roadmap

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
