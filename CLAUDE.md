# CLAUDE.md — `vanishd`

> Gerado a partir do template `git/_templates/CLAUDE-projeto.md`
> Este agente roda via **Claude Code** e tem acesso ao filesystem e ferramentas de terminal.

---

## O que é este projeto

Compartilhamento de secrets zero-knowledge com links de uso único — o servidor nunca acessa o plaintext.

**Por que existe:** Demonstra arquitetura zero-knowledge com client-side AES-GCM, one-time token pattern, e pipeline DevOps completo sobre uma aplicação de segurança real.

**Competências DevOps demonstradas neste projeto:**
- Arquitetura zero-knowledge: client-side crypto com Web Crypto API nativa
- CI/CD multi-stage: lint → SAST → build → scan → release → publish → deploy
- Container scanning com Trivy + SAST com Bandit
- Security hardening: rate limiting, secure headers, delete atômico, logging seguro
- Self-hosted end-to-end: GHCR + GitHub Actions free tier + deploy via Docker Compose

---

## Stack da aplicação

- **Linguagem/runtime:** Python 3.12 / Flask
- **Banco de dados:** SQLite (stdlib `sqlite3`, volume Docker para persistência)
- **Servidor:** Waitress (produção)
- **Frontend:** HTML + CSS + JavaScript vanilla — Web Crypto API nativa, zero dependências JS externas

---

## Stack DevOps

- **CI/CD:** GitHub Actions
  - Stages: lint (flake8 + hadolint) → SAST (bandit) → build → scan (Trivy) → release (auto-tag semver) → publish (GHCR) → deploy
- **Registry:** GHCR (`ghcr.io/NatanRigailo/vanishd`)
- **Qualidade:** SonarCloud
- **Scan:** Trivy (CVEs na imagem)
- **Dependências:** Dependabot (pip semanal + actions semanal)
- **Reverse proxy:** não configurado ainda (Traefik/Nginx quando for para produção)
- **Observabilidade:** apenas `/healthz` por enquanto — Prometheus+Grafana fora do escopo inicial

---

## Como funciona — arquitetura zero-knowledge

### Modo link completo (chave no fragment)
```
[Browser remetente]                    [Servidor]              [Browser destinatário]
   gera chave AES-256-GCM
   cifra o secret (AES-GCM)
   POST /api/secrets {ciphertext} ──► armazena blob cifrado
   recebe {id}                        nunca viu o plaintext
   monta URL: /s/{id}#{base64(chave)}
                                                               abre o link
                                                               extrai chave do #fragment
                                                               GET /api/secrets/{id} ──► retorna + deleta
                                                               decifra localmente com a chave
                                                               exibe o secret
                                                               (link inválido para sempre)
```

### Modo senha (PBKDF2)
- Remetente define uma senha; JS deriva chave AES via PBKDF2 (200k iterações, SHA-256)
- Salt aleatório armazenado com o ciphertext (não é segredo)
- Link não contém a chave — destinatário digita a senha para derivar e decifrar
- Servidor armazena: `ciphertext + salt` — continua sem ver o plaintext

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `SECRET_KEY` | gerado em runtime | Chave Flask para sessão/CSRF |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_TTL_SECONDS` | `604800` | TTL máximo permitido (7 dias) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Requests por minuto por IP no endpoint de leitura |
| `RATE_LIMIT_POST_PER_MINUTE` | `10` | Requests por minuto por IP no endpoint de escrita |
| `MAX_CONTENT_LENGTH` | `65536` | Tamanho máximo do body da requisição (bytes) |
| `CLEANUP_INTERVAL_SECONDS` | `3600` | Intervalo do job de limpeza de secrets expirados |
| `DATABASE_PATH` | `/data/vanishd.db` | Caminho do arquivo SQLite |

---

## Roadmap

As milestones e issues são gerenciadas no GitHub: https://github.com/NatanRigailo/vanishd/milestones

### v0.1 — Fundação
- [ ] Estrutura inicial do projeto (pastas, arquivos base)
- [ ] Dockerfile multi-stage non-root
- [ ] Flask app skeleton com `/healthz` e logging estruturado
- [ ] SQLite schema inicial

### v0.2 — Core Feature
- [ ] Client-side AES-GCM encryption via Web Crypto API
- [ ] API POST `/api/secrets` — receber e armazenar blob cifrado
- [ ] API GET `/api/secrets/:id` — one-time read com delete atômico
- [ ] Modo link completo — chave AES no URL fragment
- [ ] Modo senha — PBKDF2 deriva chave AES a partir de senha do usuário
- [ ] UI mínima — create e view de secrets

### v0.3 — CI Pipeline
- [ ] Lint stage (flake8 + hadolint)
- [ ] SAST com bandit
- [ ] Build da imagem Docker com cache
- [ ] Container scan com Trivy
- [ ] Dependabot para dependências Python e Actions
- [ ] SonarCloud quality gate no CI

### v0.4 — Security Hardening
- [ ] Rate limiting no endpoint de leitura
- [ ] Secure HTTP headers (CSP, HSTS, X-Frame-Options)
- [ ] Cleanup job para secrets expirados
- [ ] Logging de acessos sem expor conteúdo sensível

### v0.5 — Release & Deploy
- [ ] Auto-tag semver no merge para main
- [ ] Publish automático da imagem para GHCR
- [ ] Deploy workflow via docker compose no host
- [ ] README final com badges, quick start e roadmap versionado

---

## Estado atual

**Versão:** v1.0 em andamento

**Milestones concluídas:**
- ✅ v0.1 — Fundação: estrutura, Dockerfile multi-stage non-root, Flask skeleton, SQLite schema
- ✅ v0.2 — Core Feature: AES-256-GCM client-side, POST/GET /api/secrets, modo link + modo senha, UI mínima
- ✅ v0.3 — CI Pipeline: lint (flake8+hadolint), SAST (bandit), build+Trivy, SonarCloud, Dependabot, CODEOWNERS
- ✅ v0.4 — Security Hardening: rate limiting, secure headers + CSP sem unsafe-inline, cleanup job, logging seguro
- ✅ v0.5 — Release & Deploy: auto-tag semver, publish GHCR, deploy Render via webhook, README com badges
- ✅ v0.6 — Quality & Dev Experience: pre-commit hooks, actionlint, JS code smells, testes (97% coverage), /healthz DB check, rate limit POST, log injection sanitization
- ✅ v0.7 — Production Ready: suporte PostgreSQL via DATABASE_URL (_Conn wrapper, psycopg2-binary), pip-audit, gitleaks, fix libpq5 runtime (Render+Supabase via pooler IPv4 port 6543)

**Issues avulsas em aberto:**
- Issue #64: security hotspot CSRF — avaliar proteção CSRF no POST /api/secrets (SonarCloud S4502)

**v1.0 — Em andamento:**
- Issue #49: DAST com OWASP ZAP no pipeline
- Issue #46: padronizar frontend com design system do portfólio
- Issue #56: páginas de erro customizadas (404, 500, 413, 429)
- Issue #55: histórico de secrets criados via localStorage
- Issue #60: acessibilidade — associar label ao controle de modo na create page

**Próximas milestones:**
- v1.1 — UX Polish: botão de revelação (expira só ao confirmar leitura) — issue #57

**Lições aprendidas:**
- `build-and-scan` precisa de `if: always() && ... (sast.result == 'success' || sast.result == 'skipped')` para funcionar em PRs do Dependabot
- SonarCloud PR decoration exige `pull-requests: write` no job + permissão "Pull requests: Read and write" no GitHub App do SonarCloud
- CSP sem `unsafe-inline`: mover todo JS inline para arquivos estáticos; passar dados do servidor via `data-*` attributes
- pytest-cov gera paths absolutos; SonarCloud precisa de `relative_files = True` no `.coveragerc`
- psycopg2-binary sem wheel para Python 3.14 — builder precisa de `libpq-dev build-essential`; stage final precisa de `libpq5`
- Supabase no Render: DNS resolve IPv6, Render free tier não tem IPv6 outbound — usar connection pooler (porta 6543, IPv4)

---

## Papel deste agente

Este agente é um **executor** — não apenas consultor. Ele traduz o roadmap em entregas reais
no repositório GitHub, trabalhando junto comigo em ciclos de discussão → execução → revisão.

### Fluxo de trabalho padrão

1. **Discussão** — conversamos sobre a próxima milestone ou tarefa, alinhamos o que será feito e como
2. **Planejamento** — o agente propõe as issues a criar, com título, descrição e labels, e aguarda minha aprovação
3. **Execução** — após aprovação, o agente:
   - Cria a branch (`feat/`, `fix/`, `chore/` conforme o tipo)
   - Implementa as mudanças com commits atômicos e mensagens em Conventional Commits
   - Abre o PR linkando a issue, com descrição clara do que foi feito e checklist de revisão
4. **Revisão** — eu reviso o PR e faço o merge. O agente não faz merge nunca.
5. **Atualização** — após merge, o agente atualiza o estado no CLAUDE.md se necessário

### O que o agente faz autonomamente
- Ler o estado do repositório (`git log`, `git status`, `gh issue list`, `gh pr list`)
- Criar e trocar de branches
- Escrever e editar arquivos
- Fazer commits (atômicos, com mensagens Conventional Commits)
- Criar issues via `gh issue create`
- Abrir PRs via `gh pr create`
- Rodar lint, testes e build localmente para validar antes de abrir o PR

### O que o agente pergunta antes de fazer
- Criar issues em lote (apresenta a lista completa para aprovação antes de executar)
- Qualquer mudança que afete contratos públicos da aplicação (rotas, variáveis de ambiente, schema)
- Escolhas de arquitetura que não estavam previstas no roadmap

### O que o agente nunca faz
- Merge de PRs — sempre responsabilidade minha
- Push direto em `main`
- Deletar branches remotas sem confirmação
- Alterar secrets, tokens ou credenciais reais

---

## Convenções do repositório

- **Branches:** `feat/descricao-curta`, `fix/descricao-curta`, `chore/descricao-curta`
- **Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`, `refactor:`)
- **PRs:** título no formato Conventional Commits, descrição com contexto + checklist
- **Issues:** linkadas no PR com `Closes #N`
- **Labels:** `feature`, `bug`, `ci`, `docs`, `security`, `infra`

---

## Pré-requisitos do ambiente

Para que o agente opere corretamente via Claude Code:
- `git` configurado com acesso ao repositório
- `gh` CLI autenticado (`gh auth status`)
- Docker disponível localmente (para builds de validação)
- Variáveis do `.env.example` copiadas para `.env` com valores de dev

---

## Referências

- Padrões gerais: `../CLAUDE.md`
- Projeto de referência: `../mfa-app`
- Issues: https://github.com/NatanRigailo/vanishd/issues
- Milestones: https://github.com/NatanRigailo/vanishd/milestones
