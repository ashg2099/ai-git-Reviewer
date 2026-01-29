import pytest
import torch
from ai_gitreviewer.core.nlp_engine import NLPEngine

@pytest.fixture(scope="module")
def nlp_engine():
    """Fixture to load the model once for all tests in this file."""
    return NLPEngine()

def test_engine_initialization(nlp_engine):
    """Verify the model and tokenizer load correctly."""
    assert nlp_engine.model is not None
    assert nlp_engine.tokenizer is not None
    assert len(nlp_engine.bad_patterns) > 0

def test_high_similarity_detection(nlp_engine):
    """Test that a blatantly bad snippet triggers the correct pattern."""
    bad_code = "password = 'admin123'  # Hardcoded admin pass"
    results = nlp_engine.analyze(bad_code, threshold=0.7)
    
    # Check if the AI Insight contains the word 'credentials' or 'secret'
    found = any("credentials" in issue.lower() or "secret" in issue.lower() for issue in results)
    assert found, f"AI failed to detect hardcoded credentials in: {results}"

def test_low_similarity_rejection(nlp_engine):
    """Test that safe, boilerplate code does NOT trigger AI insights."""
    # Using a very standard, long-form boilerplate to move away from 'generic' math
    safe_code = """
def get_user_subscription_status(user_id, database_connection):
    # This is a standard database query with no security risks
    query = "SELECT status FROM subscriptions WHERE user_id = ?"
    cursor = database_connection.cursor()
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result if result else "inactive"
"""
    results = nlp_engine.analyze(safe_code, threshold=0.90)
    
    assert len(results) == 0, f"AI raised false positive on safe code: {results}"

def test_semantic_discrimination(nlp_engine):
    """
    Test if AI can distinguish between unsafe file opening and 
    proper context manager usage.
    """
    unsafe = "f = open('data.txt', 'r'); content = f.read()"
    safe = "with open('data.txt', 'r') as f: content = f.read()"
    
    # Helper to get the raw score for the 'unsafe file handling' pattern
    def get_score(code):
        code_emb = nlp_engine._get_embeddings([code])
        pattern_emb = nlp_engine.pattern_embeddings[1:2]
        return torch.nn.functional.cosine_similarity(code_emb, pattern_emb).item()

    unsafe_score = get_score(unsafe)
    safe_score = get_score(safe)
    
    print(f"\nUnsafe Score: {unsafe_score:.4f} vs Safe Score: {safe_score:.4f}")
    assert unsafe_score > safe_score

def test_empty_input_handling(nlp_engine):
    """Ensure the engine handles empty or short strings gracefully."""
    assert nlp_engine.analyze("") == []
    assert nlp_engine.analyze("   ") == []
    assert nlp_engine.analyze("x = 1") == []