# 🧠 AI-GitReviewer

> A professional-grade, hybrid code auditor that doesn't just find bugs — it fixes them.

AI-GitReviewer combines three layers of intelligence to review your Python code:

- **Layer 1 — Static Analysis**: Deep AST parsing with regex fallback
- **Layer 2 — Semantic AI**: CodeBERT understands code meaning, not just syntax
- **Layer 3 — Generative AI**: Llama-3 via Groq provides production-ready refactors and architectural critique

---

## ✨ What It Detects

| Category | What's Caught |
|---|---|
| 🔴 Security | `eval()` usage, hardcoded secrets & API keys |
| 🔴 Logic | Mutable default arguments, recursion without base case |
| 🟠 Stability | Bare `except:` blocks, blocking I/O in async functions |
| 🟠 Complexity | Functions with more than 5 arguments |
| 🟡 Best Practices | `== None` instead of `is None`, `print()` instead of logging |
| 🔵 AI Insights | Weak crypto (MD5), poor naming conventions, unsafe file handling |

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher → [Download](https://www.python.org/downloads/)
- Git → [Download](https://git-scm.com/downloads/)
- A free Groq API key → [Get one here](https://console.groq.com)

### Install the package

```bash
pip install git+https://github.com/ashg2099/ai-git-Reviewer.git
```

That's it — the `ai-review` command is now available globally on your system. No need to clone the repo.

---

## ⚙️ One-time Setup

**Step 1 — Get a free Groq API key** at [https://console.groq.com](https://console.groq.com)

**Step 2 — Set your key globally** (works across every project, forever):

```bash
echo "GROQ_API_KEY=your_gsk_key_here" >> ~/.ai-gitreviewer.env
```

**Step 3 — Verify the connection:**

```bash
ai-review status
```

You should see:
✅ Connected to Groq API successfully.
Model in use: llama-3.1-8b-instant

> **Alternative — Per project setup:** If you prefer to set the key per project, create a `project.env` file in the root of each repo you want to scan:
> ```
> GROQ_API_KEY=your_gsk_key_here
> ```
> ⚠️ Never commit `project.env` — it's already in `.gitignore`

---

## 🚀 Quick Start

### Review code before committing (recommended workflow)

```bash
# Navigate to any Python project on your machine
cd your-python-project

# Stage the files you want to review
git add your_file.py

# Run the review — report opens in your browser automatically
ai-review review
```

### Scan an entire repository

```bash
cd your-python-project
ai-review full-scan
```

All reports are saved to `~/.ai-gitreviewer/reports/` and open automatically in your browser. You'll get:
- Per-issue code snippets with line numbers
- AI-generated production-ready fixes
- Architectural critique of your project structure

---

## 📟 All Commands

| Command | Description |
|---|---|
| `ai-review status` | Check your Groq API connection |
| `ai-review review` | Review staged changes only (pre-commit) |
| `ai-review full-scan` | Scan every Python file in the project |
| `ai-review version` | Show the current version |

---

## 🧪 Running Tests

```bash
pytest -v
```

Run only fast static tests (no API key needed):
```bash
pytest tests/test_analyzer.py -v
```

---

## 📁 Project Structure

ai-git-Reviewer/
├── src/
│   └── ai_gitreviewer/
│       ├── cli.py               # Typer CLI commands
│       ├── main.py          # Full scan entry point
│       └── core/
│           ├── analyzer.py      # 3-layer analysis engine
│           ├── nlp_engine.py    # CodeBERT + Groq integration
│           ├── reporter.py      # HTML report generator
│           ├── git_utils.py     # Git diff parsing
│           └── cache_manager.py # File change detection
├── tests/
├── pyproject.toml
├── requirements.txt
└── project.env.example


---

## 📈 Roadmap

- [x] Phase 1 — AST static analysis with regex fallback
- [x] Phase 2 — CodeBERT semantic similarity engine
- [x] Phase 3 — Llama-3 generative refactors via Groq
- [ ] Phase 4 — GitHub Actions pre-commit integration
- [ ] Phase 5 — Support for JavaScript / TypeScript

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes and run `pytest`
4. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.