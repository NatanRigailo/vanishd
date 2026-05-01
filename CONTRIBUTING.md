# Contributing to vanishd

Thanks for your interest in contributing. This document covers how to get started, the project conventions, and an honest note about how this project is developed.

---

## How this project is developed

**vanishd is intentionally built by AI agents.**

The primary developer uses [Claude Code](https://claude.ai/code) — Anthropic's CLI agent — to implement features, write infrastructure, and maintain the codebase. This is not a shortcut: it is the point. The project exists as a portfolio piece that demonstrates DevOps practices, and the AI-assisted workflow is part of what is being showcased.

### CLAUDE.md

The file [`CLAUDE.md`](./CLAUDE.md) at the root of this repository is not documentation for humans — it is the instruction set for the AI agent. It defines:

- What the project is and why it exists
- The technology stack and DevOps conventions
- The agent's workflow (how it creates branches, commits, and PRs)
- Constraints (budget zero, self-hosted only, no cloud managed services)
- What the agent does autonomously vs. what requires human approval

If you want to contribute using an AI agent, reading `CLAUDE.md` first will give the agent the context it needs to work consistently with the rest of the codebase.

### What this means for human contributors

Human contributions are welcome. Just know that the code style, commit format, and PR structure are designed to be consistent with the AI-assisted workflow described in `CLAUDE.md`. Following the same conventions keeps the history clean and the project coherent.

---

## Getting started

**Prerequisites**

```bash
git --version   # 2.x+
docker --version
make --version
```

**Run locally**

```bash
git clone https://github.com/NatanRigailo/vanishd.git
cd vanishd
cp .env.example .env
make up         # builds image and starts container on port 8080
```

Open `http://localhost:8080` to use the app.

**Other useful commands**

```bash
make build   # build the Docker image
make lint    # run flake8 + hadolint
make logs    # follow container logs
make down    # stop and remove container
make clean   # stop container and remove image + volume
```

---

## Contribution workflow

1. Fork the repository and create a branch:
   ```
   feat/short-description
   fix/short-description
   chore/short-description
   docs/short-description
   ```

2. Make your changes with atomic commits following [Conventional Commits](https://www.conventionalcommits.org):
   ```
   feat: add expiry countdown to view page
   fix: handle empty ciphertext in POST /api/secrets
   docs: add rate limiting notes to README
   ```

3. Run lint before opening a PR:
   ```bash
   make lint
   ```

4. Open a PR with a clear title (Conventional Commits format) and a description that explains what changed and why. Link the related issue with `Closes #N`.

5. PRs are merged by the project maintainer. The AI agent does not merge PRs.

---

## Reporting bugs

Open an issue with the label `bug`. Include steps to reproduce, expected behavior, and actual behavior.

## Reporting security vulnerabilities

**Do not open a public issue for security vulnerabilities.**

Use [GitHub Security Advisories](https://github.com/NatanRigailo/vanishd/security/advisories/new) to report privately. Disclosures will be reviewed and acknowledged within 7 days.
