import ast
import re
from .nlp_engine import NLPEngine

class ReviewerEngine:
    def __init__(self, use_ai=True):
        self.use_ai = use_ai
        self.nlp_engine = None
        if self.use_ai:
            self.nlp_engine = NLPEngine()

    def _clean_diff(self, diff_content):
        added_lines = []
        for line in diff_content.split('\n'):
            # Skip '+++' and '---' headers, but keep '+' lines
            if line.startswith('+') and not line.startswith('+++'):
                # Strip the '+' but keep the original indentation
                added_lines.append(line[1:])
        return "\n".join(added_lines)

    def analyze_content(self, content):
        """Handles both raw file content and Git diffs."""
        file_issues = []
        
        is_diff = content.startswith('diff --git') or content.startswith('index ')
        
        if is_diff:
            print("DEBUG: Processing as Git Diff")
            clean_code = self._clean_diff(content)
        else:
            clean_code = content

        if not clean_code.strip():
            print("DEBUG: Clean code is empty, skipping analysis.")
            return file_issues

        # --- LEVEL 1: STRUCTURAL ANALYSIS (AST) ---
        try:
            tree = ast.parse(clean_code)
            for node in ast.walk(tree):
                # Rule 1: print()
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'print':
                    file_issues.append(f"L{node.lineno}: Avoid print(). Use logging instead.")

                # Rule 2: == None
                if isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, ast.Eq):
                            for comp in node.comparators:
                                if isinstance(comp, ast.Constant) and comp.value is None:
                                    file_issues.append(f"L{node.lineno}: Use 'is None' for identity checks.")
                
                # Rule 3: eval()
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'eval':
                    file_issues.append(f"L{node.lineno}: Security Risk: 'eval()' detected.")
                
                # Rule 4: Arg count
                if isinstance(node, ast.FunctionDef):
                    arg_count = len(node.args.args)
                    if arg_count > 5:
                        file_issues.append(f"L{node.lineno}: Function '{node.name}' has too many arguments ({arg_count}).")

                # Rule 5: Mutable Default Arguments
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict)):
                            file_issues.append(f"L{node.lineno}: Dangerous mutable default argument detected in '{node.name}'. Use 'None' instead.")

                # Rule 6: Bare Except blocks
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    file_issues.append(f"L{node.lineno}: Bare 'except:' caught. Specify an exception type.")
                    
                # Rule 7: Simple Recursion Detection
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    for sub_node in ast.walk(node):
                        # If the function calls itself...
                        if isinstance(sub_node, ast.Call) and getattr(sub_node.func, 'id', None) == func_name:
                            file_issues.append(f"L{sub_node.lineno}: Structural Recursion detected in '{func_name}'.")
            
        except SyntaxError:
            # --- FALLBACK: REGEX ---
            if "print(" in clean_code:
                file_issues.append("Found print() statement. Avoid print().")
            if "== None" in clean_code:
                file_issues.append("Found '== None'. Use 'is None' for identity checks.")
            if "eval(" in clean_code:
                file_issues.append("Security Risk: 'eval()' detected.")
            if re.search(r"def\s+\w+\(.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\)", clean_code):
                 file_issues.append("Function has too many arguments.")

        # --- LEVEL 2: SEMANTIC ANALYSIS (CODEBERT) ---
        # Only run if AI is enabled and the engine was successfully loaded
        if self.use_ai and self.nlp_engine:
            try:
                if len(clean_code.strip()) > 15:
                    ai_insights = self.nlp_engine.analyze(clean_code)
                    file_issues.extend(ai_insights)
            except Exception as e:
                file_issues.append(f"AI Engine error: {str(e)}")
            
        return file_issues