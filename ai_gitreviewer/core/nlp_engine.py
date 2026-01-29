import torch
from transformers import AutoTokenizer, AutoModel

class NLPEngine:
    def __init__(self):
        # The 'Brain': microsoft/codebert-base
        self.model_name = "microsoft/codebert-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Knowledge base of patterns
        self.bad_patterns = [
            "hardcoded credentials or secret keys",
            "unsafe file handling without context manager",
            "using unsafe eval or exec functions",
            "recursive function without base case",
            "blocking I/O in async function",
            "non-descriptive variable names like a, b, c",
            "cryptographic operations using weak hashes like md5",
            "Recursive function call without a base case check, potential infinite loop",
        ]
        # Pre-compute embeddings for patterns
        self.pattern_embeddings = self._get_embeddings(self.bad_patterns)

    def _get_embeddings(self, texts):
        """Helper to turn text/code into CodeBERT math vectors."""
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        return outputs.last_hidden_state.mean(dim=1)

    def analyze(self, code_snippet, threshold=0.90):
        if not code_snippet.strip() or len(code_snippet) < 15:
            return []

        code_embedding = self._get_embeddings([code_snippet])
        cos = torch.nn.CosineSimilarity(dim=1)
        scores = cos(code_embedding, self.pattern_embeddings)
        
        # Create a list of (score, pattern) tuples
        matches = []
        for i, score in enumerate(scores):
            val = score.item()
            if val > threshold:
                matches.append((val, self.bad_patterns[i]))
                
        # 1. Sort by highest confidence first
        matches.sort(key=lambda x: x[0], reverse=True)
        
        # 2. Pick only the top unique match to avoid "Insight Spam"
        ai_findings = []
        if matches:
            best_score, best_pattern = matches[0]
            ai_findings.append(f"AI Insight ({best_score:.2f}): This logic resembles '{best_pattern}'")
        
        return ai_findings