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

**Requires Python 3.9+**

### Option A — Install directly from GitHub (recommended)
```bash
pip install git+https://github.com/ashg2099/ai-git-Reviewer.git
```

### Option B — Clone and install locally
```bash
git clone https://github.com/ashg2099/ai-git-Reviewer.git
cd ai-git-Reviewer
pip install -e ".[dev]"
```

---

## ⚙️ Setup

The tool uses Groq's API to power Llama-3 refactors. You need a free API key.

1. Get a free key at [https://console.groq.com](https://console.groq.com)
2. Set up your Groq API key — choose one option:

**Option A — Global (recommended):** Set once, works in every project:
```bash
echo "GROQ_API_KEY=your_gsk_key_here" >> ~/.ai-gitreviewer.env
```

**Option B — Per project:** Create a `project.env` in each repo you scan:
```bash
cp project.env.example project.env
# then add your key inside project.env

> ⚠️ Never commit `project.env` — it's already in `.gitignore`

---

## 🚀 Usage

### 1. Check your Groq connection
```bash
ai-review status
```

### 2. Review staged changes (pre-commit check)
Stage your files first, then run:
```bash
git add your_file.py
ai-review review
```
This only reviews code you are about to commit — perfect as a pre-commit gate.

### 3. Full repository audit
```bash
ai-review full-scan
```
Scans every Python file and generates an architectural critique of your entire project structure.

### 4. Check version
```bash
ai-review version
```

All commands open an **HTML report** in your browser automatically with:
- Per-issue code snippets
- AI-generated fixes
- Architectural recommendations

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
│       ├── cli.py              # Typer CLI commands
│       ├── main.py         # Full scan entry point
│       └── core/
│           ├── analyzer.py     # 3-layer analysis engine
│           ├── nlp_engine.py   # CodeBERT + Groq integration
│           ├── reporter.py     # HTML report generator
│           ├── git_utils.py    # Git diff parsing
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