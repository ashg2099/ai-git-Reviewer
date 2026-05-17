import os
import torch
import json
import re
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

# Check project-level first, then fall back to global user config
load_dotenv("project.env")
load_dotenv(Path.home() / ".ai-gitreviewer.env")
from transformers import AutoTokenizer, AutoModel

class NLPEngine:
    def __init__(self):
        # --- 1. GROQ CLOUD SETUP ---
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.llama_model = "llama-3.1-8b-instant"
        print(f"✅ NLPEngine: Groq {self.llama_model} Ready")

        # --- 2. CODEBERT SETUP (Local) ---
        self.codebert_name = "microsoft/codebert-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.codebert_name)
        self.bert_model = AutoModel.from_pretrained(self.codebert_name)
        
        self.bad_patterns = [
            "hardcoded credentials or secret keys",
            "unsafe file handling without context manager",
            "using unsafe eval or exec functions",
            "recursive function without base case",
            "blocking I/O in async function",
            "non-descriptive variable names",
            "weak cryptographic hashes like md5",
        ]
        self.pattern_embeddings = self._get_embeddings(self.bad_patterns)

    def _get_embeddings(self, texts):
        """Helper for CodeBERT Embeddings."""
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    def analyze(self, code_snippet, threshold=0.90):
        """LEVEL 2: Local AI analysis using CodeBERT."""
        if not code_snippet.strip() or len(code_snippet) < 15:
            return []
        
        try:
            code_embedding = self._get_embeddings([code_snippet])
            cos = torch.nn.CosineSimilarity(dim=1)
            scores = cos(code_embedding, self.pattern_embeddings)
            
            matches = [self.bad_patterns[i] for i, s in enumerate(scores) if s.item() > threshold]
            return [f"CodeBERT Insight: Logic resembles '{m}'" for m in matches[:1]]
        except Exception as e:
            print(f"CodeBERT Error: {e}")
            return []

    def get_batch_refactor(self, filename, issues_summary, project_context=""):
        prompt = f"""
        ROLE: You are an Elite Python Architect and Cyber-Security Lead. Your goal is to provide high-quality, production-ready code fixes. You must ensure that every fix is a complete, functional replacement for the problematic block.

        PROJECT CONTEXT: {project_context}
        FILE CONTEXT: {filename}
        DETECTED ISSUES: {issues_summary}

        ### EXECUTION GUIDELINES
        1. **Atomic Replacements**: Provide the smallest functional block of code that resolves the issue. For complexity or signature issues (like too many arguments), replace the entire function body and signature.
        2. **Architectural Best Practices**: If an issue is structural (Complexity/Args), use modern Python patterns like @dataclass, TypedDict, or argument grouping.
        3. **Security-First**: For "Security" issues, apply OWASP Python best practices.
        4. **Dependency Management**: If a fix requires a new import (e.g., `import logging`), prepend it to the 'fix' string on a new line.
        5. **No Hallucination**: If the code snippet provided is too small to understand the logic, return "Manual review recommended: context insufficient."
        6. **Syntactic Correctness**: Ensure all quotes are escaped and indentation matches standard Python (4 spaces).

        ### FORMATTING RULES
        - Return ONLY a valid JSON object.
        - NO markdown formatting (no backticks).
        - Keys: ID numbers from 'DETECTED ISSUES' as strings.
        - Values: A JSON object with these EXACT keys:
            - "thinking": (String) One sentence on how this fix solves the core architectural problem.
            - "fix": (String) The actual code. This MUST be a single string. Use \n for new lines. Never use nested objects.
            - "insight": A detailed explanation for the developer covering: (1) the precise technical reason this is a problem, (2) one concrete real-world consequence if left unfixed — name actual outcomes like data loss, RCE, silent corruption, or OOM crash, not vague risks, and (3) the exact condition under which a senior engineer could reasonably leave this unfixed. Write it as flowing prose in 3-4 sentences. No bullet points.
        
        ### ESCAPING RULE (CRITICAL)
        - If the code contains an f-string with a newline (e.g., f"\\n"), you must escape it correctly for JSON. 
        - DO NOT use nested objects in the "fix" field.

        JSON OUTPUT:
        """
        
        try:
            print(f"⚡ Groq Cloud is refactoring {filename}...")
            # 2. Update: Use Groq SDK completion instead of requests.post
            chat_completion = self.client.chat.completions.create(
                model=self.llama_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2048,
                response_format={"type": "json_object"} 
            )
            
            raw_text = chat_completion.choices[0].message.content.strip()
            return json.loads(raw_text)

        except Exception as e:
            print(f"Groq Refactor Error: {e}")
            return {}
        
    def get_architecture_review(self, project_tree, project_context=""):
        """Provides a high-level architectural critique of the project structure."""
        prompt = f"""
        ROLE: You are an Elite Python Architect. Review the following project structure.
        
        PROJECT CONTEXT: {project_context}
        
        DIRECTORY STRUCTURE:
        {project_tree}
        
        ### TASK:
        Provide a professional architectural critique of the project layout. 
        1. **Structure Evaluation**: Is the project organized logically (e.g., Separation of Concerns)?
        2. **Scalability**: Will this folder structure hold up as the project grows?
        3. **Best Practices**: Are there missing standard directories (tests, docs) or files?
        4. **Recommendations**: Suggest 1-2 specific structural improvements if necessary.

        FORMAT: Use Markdown with bold headers. Keep it concise (max 250 words).
        """

        try:
            # 3. Update: Use Groq SDK completion
            chat_completion = self.client.chat.completions.create(
                model=self.llama_model,
                messages=[
                    {"role": "system", "content": "You are a Senior Software Architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Architecture analysis unavailable: {str(e)}"