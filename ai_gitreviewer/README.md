# 🧠 AI-GitReviewer

AI-GitReviewer is a hybrid intelligent code auditor that combines deep structural analysis (AST) with semantic deep learning (CodeBERT). It doesn't just look for broken syntax; it understands the "vibe" of your code to catch security risks and anti-patterns that traditional linters miss.

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

### 🤖 Phase 3: Automated Refactoring (Coming soon)
[ ] NLP-based suggestions: Using a Generative Model (like GPT or T5) to suggest better variable/function names.

[ ] AI-Suggested Fixes: Not just flagging issues, but providing the corrected code block.

[ ] DevOps Integration: Packaged as a GitHub Action for automated Pull Request reviews.

[ ] Configuration: A .reviewer.yaml file to allow users to toggle specific AI rules.