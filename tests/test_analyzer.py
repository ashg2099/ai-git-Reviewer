import pytest
from ai_gitreviewer.core.analyzer import ReviewerEngine

def test_reviewer_catches_print():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = "+ print('hello world')"
    issues = engine.analyze_content(fake_diff)
    
    assert len(issues) >= 1
    # Fix: Access ['issue'] key
    assert any("print" in issue['issue'].lower() for issue in issues)

def test_reviewer_ignores_comments():
    engine = ReviewerEngine(use_ai=False) 
    fake_diff = "+ # This is a print statement in a comment"
    issues = engine.analyze_content(fake_diff)
    assert len(issues) == 0

def test_reviewer_catches_none_comparison():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = "+ if x == None:"
    issues = engine.analyze_content(fake_diff)
    # Fix: Access ['issue'] key
    assert any("None" in issue['issue'] for issue in issues)
    
def test_reviewer_catches_eval():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = "+ result = eval('1 + 1')"
    issues = engine.analyze_content(fake_diff)
    # Fix: Access ['issue'] key
    assert any("Security Risk" in issue['issue'] for issue in issues)

def test_reviewer_ignores_strings():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = "+ my_string = 'This is a print statement in a string'"
    issues = engine.analyze_content(fake_diff)
    assert len(issues) == 0

def test_reviewer_multi_line_diff():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = """
+ print('Debug log')
+ if user == None:
+     eval(user_input)
"""
    issues = engine.analyze_content(fake_diff)
    assert len(issues) == 3
    
def test_reviewer_catches_too_many_args():
    engine = ReviewerEngine(use_ai=False)
    fake_diff = "+ def high_complexity_func(a, b, c, d, e, f): pass"
    issues = engine.analyze_content(fake_diff)
    # Fix: Access ['issue'] key
    assert any("too many arguments" in issue['issue'].lower() for issue in issues)

def test_reviewer_catches_recursion():
    # Use use_ai=True if your engine uses AST for recursion detection
    engine = ReviewerEngine(use_ai=True)
    recursive_code = """
def calculate_factorial(n):
    return n * calculate_factorial(n - 1)
"""
    issues = engine.analyze_content(recursive_code)
    
    # Fix: Access ['issue'] key and handle dict structure
    found = any(keyword in issue['issue'].lower() for issue in issues 
                for keyword in ["recursion", "recursive", "logic", "unsafe"])
    assert found is True