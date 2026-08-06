# Contributing to Dataset Genome

Thank you for your interest in contributing to **Dataset Genome**! This project is an open-source scientific reasoning benchmark platform, and contributions of all kinds are welcome.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Commit Message Convention](#commit-message-convention)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this standard. Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### 🐛 Reporting Bugs
Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template. Include:
- Python version, OS, and environment details
- Minimal reproduction steps
- Expected vs. actual behavior
- Relevant logs or tracebacks

### 💡 Suggesting Features
Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template. Describe:
- The problem you want to solve
- Your proposed solution
- Any alternatives you considered

### 📖 Improving Documentation
Documentation improvements are always welcome:
- Fix typos or unclear explanations in `docs/`
- Add missing docstrings to Python modules
- Improve `README.md` sections

### 🧪 Adding Tests
The backend has 188 tests in `backend/tests/`. New tests must:
- Follow the existing `pytest` conventions
- Cover both success and failure paths
- Not require live API keys (use mocks)

### 🔬 Scientific Domain Additions
The benchmark currently covers 10 scientific domains. New domain contributions must:
- Include template seed data in `backend/app/dataset_generator/templates.py`
- Pass validation with the existing `BenchmarkValidator`
- Include domain-specific evaluation metrics

---

## Development Setup

### Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run tests
cd ..
pytest backend/tests/ -v
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Full Pipeline

```bash
cp .env.example .env
# Add GOOGLE_API_KEY or OPENAI_API_KEY
python demo.py
```

---

## Pull Request Process

1. **Fork** the repository and create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** following the [coding standards](#coding-standards) below.

3. **Run tests** and ensure they pass:
   ```bash
   pytest backend/tests/ -v
   ```

4. **Update documentation** if your change affects behavior or adds new functionality.

5. **Commit** using the [conventional commits](#commit-message-convention) format.

6. **Submit a Pull Request** against `main` using the PR template.

7. A maintainer will review your PR within a reasonable timeframe.

> ⚠️ **Important:** The backend is currently in a **frozen** state for the HackIndia submission. Feature PRs touching `backend/` will be reviewed after the hackathon.

---

## Coding Standards

### Python

- **Style:** Follow [PEP 8](https://peps.python.org/pep-0008/)
- **Type hints:** Required on all public functions and class methods
- **Docstrings:** Google-style docstrings on all public classes and functions
- **Max line length:** 100 characters

```python
def generate_sample(
    domain: str,
    difficulty: str = "Medium",
    index: int = 1,
) -> BenchmarkSample:
    """Generate a single benchmark sample.

    Args:
        domain: The scientific domain (e.g., "Agriculture").
        difficulty: One of Easy, Medium, Hard, Expert.
        index: Sequential index used as a uniqueness hint.

    Returns:
        A validated BenchmarkSample instance.

    Raises:
        GenerationExhaustedError: If all retry attempts fail.
    """
```

### TypeScript / React

- **Style:** Follow the existing ESLint configuration (`frontend/eslint.config.mjs`)
- **Type safety:** No `any` types
- **Components:** Functional components with explicit prop types

---

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `test` | Adding or updating tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Build process, dependency updates, etc. |

**Examples:**

```
feat(benchmark): add Climate Science domain templates
fix(llm): handle Gemini rate limit with exponential backoff
docs(readme): update installation instructions for macOS
test(benchmark): add validation tests for duplicate detection
```

---

## Reporting Bugs

Before filing a bug report, please:

1. **Search existing issues** to avoid duplicates
2. **Test with the latest version** from `main`
3. **Collect logs** from the failing run

Submit bugs via [GitHub Issues](https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes/issues) using the Bug Report template.

---

## Suggesting Features

Feature suggestions are tracked via [GitHub Issues](https://github.com/HackIndiaXYZ/adaption-autoscientist-challenge-part-2-60000-prize-pool-surabhicodes/issues). Please use the Feature Request template and describe:

- **Problem:** What problem does this solve?
- **Solution:** How should it work?
- **Scope:** Which component(s) does it affect?

---

*Thank you for contributing to Dataset Genome! Every contribution, no matter how small, helps improve scientific AI research.*
