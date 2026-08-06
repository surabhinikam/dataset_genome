# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| v1.0.x  | ✅ Active |

---

## Reporting a Vulnerability

The Dataset Genome team takes security seriously. If you discover a security vulnerability in this project, please follow the responsible disclosure process below.

### ⚠️ Do NOT open a public GitHub issue for security vulnerabilities.

### How to Report

1. **Email the maintainer directly** with a description of the vulnerability.
2. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
3. You will receive an acknowledgement within **48 hours**.
4. We will work with you to validate and fix the vulnerability.
5. We will credit you in the fix unless you prefer to remain anonymous.

---

## What Counts as a Security Vulnerability?

Please report:

- **API key exposure** — accidental inclusion of secrets in code or config
- **Authentication bypass** — any way to bypass API authentication
- **Injection vulnerabilities** — prompt injection, SQL injection, command injection
- **Path traversal** — unauthorized file system access via the upload endpoint
- **CORS misconfiguration** — unintended cross-origin access

---

## Out of Scope

The following are **not** considered security vulnerabilities for this project:

- Vulnerabilities in third-party dependencies (report to their maintainers)
- Issues in `export_benchmark/` output files (these are generated artifacts)
- Issues requiring physical access to the host machine

---

## Security Best Practices for Contributors

- **Never commit `.env` files** — use `.env.example` as a template
- **Never hardcode API keys** in source code
- **Use environment variables** for all secrets (see `.env.example`)
- **Keep dependencies updated** — run `pip audit` regularly
- **Review the `.gitignore`** before committing to ensure secrets are excluded

---

## Dependency Security

This project uses the following external services that require API keys:

- Google Gemini API (`GOOGLE_API_KEY`)
- OpenAI API (`OPENAI_API_KEY`)
- Anthropic API (`ANTHROPIC_API_KEY`)

All keys are loaded from environment variables and are **never** logged or included in exports.

---

*Security policy for Dataset Genome — HackIndia 2026 AutoScientist Challenge*
