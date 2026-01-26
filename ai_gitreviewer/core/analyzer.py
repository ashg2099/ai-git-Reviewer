import ast
import re

class ReviewerEngine:
    def __init__(self):
        self.issues = []

    def _clean_diff(self, diff_content):
        """Removes git '+' markers to make the code valid Python for AST."""
        added_lines = []
        for line in diff_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                # We strip leading whitespace carefully to help AST parse snippets
                added_lines.append(line[1:])
        return "\n".join(added_lines)

    def analyze_content(self, diff_content):
        """Performs deep analysis on the added code."""
        file_issues = []
        clean_code = self._clean_diff(diff_content)
        
        if not clean_code.strip():
            return file_issues

        try:
            # 1. AST Analysis
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
                # 5. Catch Mutable Default Arguments (e.g., def func(x=[]))
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        # Check if the default value is a List [] or a Dictionary {}
                        if isinstance(default, (ast.List, ast.Dict)):
                            file_issues.append(f"L{node.lineno}: Dangerous mutable default argument detected in '{node.name}'. Use 'None' instead.")
                # 6. Catch Bare Except blocks
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    file_issues.append(f"L{node.lineno}: Bare 'except:' caught. Specify an exception type (e.g., Exception) to avoid silencing system errors.")
            
        except SyntaxError:
            # 2. Regex Fallback (Crucial for snippets that aren't valid full files)
            if "print(" in clean_code:
                file_issues.append("Found print() statement. Avoid print().")
            if "== None" in clean_code:
                file_issues.append("Found '== None'. Use 'is None' for identity checks.")
            if "eval(" in clean_code:
                file_issues.append("Security Risk: 'eval()' detected.")
                
            # Simple Regex to catch functions with many commas in the signature
            # This looks for 'def' followed by anything and then at least 5 commas (6+ args)
            if re.search(r"def\s+\w+\(.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\)", clean_code):
                 file_issues.append("Function has too many arguments. Aim for 3 or less.")
            
        return file_issues