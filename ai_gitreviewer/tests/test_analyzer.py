import pytest
from ai_gitreviewer.core.analyzer import ReviewerEngine

def test_reviewer_catches_print():
    engine = ReviewerEngine()
    # We simulate a git diff string
    fake_diff = "+ print('hello world')"
    
    issues = engine.analyze_content(fake_diff)
    
    # Check that at least one issue was found
    assert len(issues) >= 1
    # FIX: Use .lower() and check for the keyword 'print'
    assert any("print" in issue.lower() for issue in issues)

def test_reviewer_ignores_comments():
    engine = ReviewerEngine()
    # This is a comment, not code
    fake_diff = "+ # This is a print statement in a comment"
    
    issues = engine.analyze_content(fake_diff)
    
    # AST should be smart enough to ignore this!
    assert len(issues) == 0

def test_reviewer_catches_none_comparison():
    engine = ReviewerEngine()
    # Note: 'if x == None:' alone is a SyntaxError for AST, 
    # so it will hit the 'except' block in your analyzer.
    fake_diff = "+ if x == None:"
    
    issues = engine.analyze_content(fake_diff)
    
    # FIX: Check for 'None' keyword to be safe
    assert any("None" in issue for issue in issues)
    
def test_reviewer_catches_eval():
    engine = ReviewerEngine()
    fake_diff = "+ result = eval('1 + 1')"
    issues = engine.analyze_content(fake_diff)
    assert any("Security Risk" in issue for issue in issues)

def test_reviewer_ignores_strings():
    """Test that it doesn't flag 'print' if it's inside a string variable."""
    engine = ReviewerEngine()
    fake_diff = "+ my_string = 'This is a print statement in a string'"
    issues = engine.analyze_content(fake_diff)
    # AST should know this is a Constant string, not a Call
    assert len(issues) == 0

def test_reviewer_multi_line_diff():
    """Test that it can handle a diff with multiple different issues."""
    engine = ReviewerEngine()
    fake_diff = """
+ print('Debug log')
+ if user == None:
+     eval(user_input)
"""
    issues = engine.analyze_content(fake_diff)
    # It should find 3 distinct issues
    assert len(issues) == 3
    
def test_reviewer_catches_too_many_args():
    engine = ReviewerEngine()
    fake_diff = "+ def high_complexity_func(a, b, c, d, e, f): pass"
    issues = engine.analyze_content(fake_diff)
    assert any("too many arguments" in issue for issue in issues)
    
def test_perfect_file_ast_path():
    """This test sends valid Python to ensure we hit the AST logic path (100% coverage)."""
    engine = ReviewerEngine()
    # No '+' markers, just valid Python code
    valid_code = """
def my_function(a, b):
    print(a)
    if b == None:
        return None
    eval("1+1")
"""
    # Note: We skip _clean_diff here by passing code directly if you want, 
    # or just wrap it in the '+' format but make it valid.
    fake_diff = "\n".join(["+" + line for line in valid_code.split("\n")])
    
    issues = engine.analyze_content(fake_diff)
    assert len(issues) >= 3 # Should catch print, == None, and eval via AST