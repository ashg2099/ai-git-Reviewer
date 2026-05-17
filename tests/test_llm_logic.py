import pytest
from unittest.mock import MagicMock, patch
from ai_gitreviewer.core.analyzer import ReviewerEngine

@pytest.fixture
def mock_engine():
    """Fixture to initialize the engine with AI enabled."""
    return ReviewerEngine(use_ai=True)

# 1. Test: Fix Suggestions
@patch('ai_gitreviewer.core.nlp_engine.NLPEngine.get_batch_refactor')
def test_llm_provides_fix_suggestion(mock_get_refactor, mock_engine):
    mock_get_refactor.return_value = {
        "0": {
            "fix": "import os\napi_key = os.getenv('API_KEY')",
            "insight": "Security risk: hardcoded key."
        }
    }

    code_snippet = "+ api_key = '12345-ABCDE'" 
    issues = mock_engine.analyze_content(code_snippet)

    assert len(issues) > 0
    assert "os.getenv" in issues[0]['suggestion']

# 2. Test: Naming Conventions
@patch('ai_gitreviewer.core.nlp_engine.NLPEngine.get_batch_refactor')
def test_llm_naming_convention_suggestion(mock_get_refactor, mock_engine):
    """Test if the LLM suggests better variable names via the NLP engine."""
    
    # We mock the NLP engine's response
    mock_get_refactor.return_value = {
        "0": {
            "fix": "user_authentication_status = True",
            "insight": "Use descriptive names."
        }
    }
    
    code_snippet = "+ x = True  # user login status"
    
    issues = mock_engine.analyze_content(code_snippet)

    if issues:
        assert "user_authentication_status" in issues[0]['suggestion']

# 3. Test: Error Handling
@patch('ai_gitreviewer.core.nlp_engine.NLPEngine.get_batch_refactor')
def test_llm_error_handling(mock_get_refactor, mock_engine):
    """Test how the engine behaves when the LLM API fails."""
    
    # Simulate an API Failure in the NLP engine
    mock_get_refactor.side_effect = Exception("API Timeout")
    
    try:
        issues = mock_engine.analyze_content("+ print('test')")
        
        assert isinstance(issues, list)
        # Even if AI fails, the AST issue should still be there
        assert len(issues) > 0 
    except Exception as e:
        pytest.fail(f"Engine crashed on LLM failure: {e}")