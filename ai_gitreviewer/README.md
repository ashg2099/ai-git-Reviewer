# 🧠 AI-GitReviewer

AI-GitReviewer is a hybrid static analysis CLI tool designed to audit Python code changes. It uses a dual-engine approach (AST + Regex) to catch security risks, logic bugs, and PEP8 violations before they are committed to your repository.

## 🛠️ Phase 1: Static Engine
The tool currently performs deep structural analysis of your code using Python's ast module, with a robust Regex fallback for partial snippets.

## 🔍 Issues Detected:
Security: Detects dangerous eval() calls that could lead to code injection.

Bug Prevention: Identifies Mutable Default Arguments (e.g., def func(x=[])) which cause shared-state bugs.

Stability: Flags Bare except: blocks that silence critical system errors.

Complexity: Monitors function signatures and flags functions with more than 5 arguments.

Best Practices: Enforces is None for identity checks and discourages print() in favor of logging.

Since you have a working Static Analysis Engine (Level 1), your README should reflect that this isn't just a "plan"—it's a functional tool.

Here is a professional, structured README.md that focuses exactly on what you have built so far, while setting the stage for the NLP phase.

🧠 AI-GitReviewer
AI-GitReviewer is a hybrid static analysis CLI tool designed to audit Python code changes. It uses a dual-engine approach (AST + Regex) to catch security risks, logic bugs, and PEP8 violations before they are committed to your repository.

🛠️ Current Capabilities (Phase 1: Static Engine)
The tool currently performs deep structural analysis of your code using Python's ast module, with a robust Regex fallback for partial snippets.

🔍 Issues Detected:
Security: Detects dangerous eval() calls that could lead to code injection.

Bug Prevention: Identifies Mutable Default Arguments (e.g., def func(x=[])) which cause shared-state bugs.

Stability: Flags Bare except: blocks that silence critical system errors.

Complexity: Monitors function signatures and flags functions with more than 5 arguments.

Best Practices: Enforces is None for identity checks and discourages print() in favor of logging.

## 🚀 How to Use
1. Installation
Clone the repository and ensure you have a Python 3.x environment.

--> git clone https://github.com/your-username/ai-git-reviewer.git
--> cd ai-git-reviewer

2. Running a Review
The tool analyzes your staged changes (code you have git add-ed).

--> python -m ai_gitreviewer review

3. Running Tests
Verified with pytest and pytest-cov for high reliability.

--> pytest --cov=ai_gitreviewer.core.analyzer

## 📈 Project Roadmap
### ✅ Phase 1: Structural Analysis (Current)
[x] AST-based logic for deep code understanding.

[x] Regex fallback for syntax-broken snippets.

[x] Line-specific error reporting.

### 🏗️ Phase 2: The "Brain" (Next Step)
[ ] Integration of CodeBERT for semantic similarity.

[ ] NLP-based suggestions for variable and function naming.

[ ] Pattern matching against a dynamic "Known Bugs" database.

### 🤖 Phase 3: Automated Refactoring
[ ] AI-suggested code fixes.

[ ] Integration as a GitHub Action.