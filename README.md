# 🧠 AI-GitReviewer

AI-GitReviewer is a professional-grade, hybrid code auditor. It combines Static Analysis (AST), Semantic Deep Learning (CodeBERT), and Generative AI (Llama-3 via Groq) to not just find bugs, but to architect their solutions.
We’ve moved beyond "flagging issues" to providing Atomic, production-ready code refactors.

## 🛠️ Phase 1: Static Engine
The tool currently performs deep structural analysis of your code using Python's ast module, with a robust Regex fallback for partial snippets.

## 🔍 Issues Detected:
1. Security: Detects dangerous eval() calls that could lead to code injection.

2. Bug Prevention: Identifies Mutable Default Arguments (e.g., def func(x=[])) which cause shared-state bugs.

3. Stability: Flags Bare except: blocks that silence critical system errors.

4. Complexity: Monitors function signatures and flags functions with more than 5 arguments.

5. Best Practices: Enforces is None for identity checks and discourages print() in favor of logging.

## 🤖 Phase 2: Semantic Brain (Complete)
This phase introduced CodeBERT, a transformer model trained on millions of code snippets, allowing the tool to perform "Semantic Reviews."

## 🧠 AI Features:
1. Contextual Understanding: Distinguishes between safe and unsafe patterns (e.g., recognizing the safety of a with open() context manager vs. a raw open()).

2. Hardcoded Secrets: Identifies high-entropy strings that resemble passwords or API keys.

3. Naming Conventions: Flags non-descriptive variable names (like a, b, c) using semantic similarity.

4. Cryptographic Audit: Detects usage of weak hashing algorithms (like MD5) based on code structure rather than just keywords.

## 🚀 How to Use
1. Installation
Clone the repository and ensure you have a Python 3.x environment.

--> git clone https://github.com/your-username/ai-git-reviewer.git
--> cd ai-git-reviewer

2. Install Dependencies
Use the requirements.txt file to install all necessary libraries

--> pip install --upgrade pip
--> pip install -r requirements.txt

3. Running a Review
The tool analyzes your staged changes (code you have git add-ed).

--> python -m ai_gitreviewer review

4. Running Tests
Verified with pytest and pytest-cov for high reliability.

--> PYTHONPATH=. python -m pytest --cov=ai_gitreviewer tests/

## 📈 Project Roadmap
### ✅ Phase 1: Structural Analysis
[x] AST-based logic for deep code understanding.

[x] Regex fallback for syntax-broken snippets.

[x] Line-specific error reporting.

### 🏗️ Phase 2: The "Brain"
[x] Integration of CodeBERT for semantic similarity.

[x] Detection of poor naming conventions via vector space mapping.

[x] High-precision thresholding (0.90) to minimize false positives.

[x] Pattern matching against a dynamic "Known Bugs" database.
Hybrid reporting (AST + AI insights in one output).

### 🤖 Phase 3: Generative Intelligence
[x] We have integrated Llama-3 (powered by Groq) to act as your team's Senior Architect.

[x] Atomic Refactors: The tool now provides full-block code replacements for detected issues.

[x] High-Speed Inference: Powered by Groq’s LPU for sub-second architectural feedback.

[x] Architectural Critique: Analyzes your entire project tree to suggest structural improvements and scalability fixes.

[x] Zero-Noise Thresholding: Combined with CodeBERT’s 0.90 similarity score, the LLM only suggests fixes when the logic is confirmed to be an anti-pattern.

## 📦 Professional Installation
AI-GitReviewer is now structured as a standard Python package. You can install it once and use it globally on any project.

1. Install via GitHub
--> pip install git+https://github.com/your-username/ai-git-reviewer.git

2. Configure your Environment
The tool requires a Groq API Key to power the "Expert Architect" refactors. Create a project.env file in the root of the project you want to scan:
--> # project.env
GROQ_API_KEY=your_gsk_key_here

## 🚀 Usage Guide
1. Standard Review (Staged Changes)
Perfect for pre-commit checks. It only analyzes the code you are about to commit.
--> ai-review review

2. Full Repository Audit
Performs a deep scan of every Python file and provides a high-level architectural critique of the folder structure.
--> ai-review full-scan

3. Testing & Coverage
--> pytest