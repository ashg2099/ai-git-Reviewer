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
            if line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])
        return "\n".join(added_lines)

    def analyze_content(self, content, filename="Unknown", project_context=""):
        file_issues = []
        
        # Check if it's actually a git diff header
        is_diff = content.startswith('diff --git') or content.startswith('--- a/')
        
        if is_diff:
            clean_code = self._clean_diff(content)
        else:
            # If scanning the whole repo, the content IS the clean code.
            clean_code = content

        lines = clean_code.split('\n')

        # --- LEVEL 1: STRUCTURAL ANALYSIS (AST) ---
        try:
            tree = ast.parse(clean_code)
            for node in ast.walk(tree):
                issue_data = None
                
                line_no = getattr(node, 'lineno', None)
                
                if line_no:
                    start_line = max(0, line_no - 5)
                    end_line = min(len(lines), line_no + 5)
                    context_window = "\n".join(lines[start_line:end_line])
                else:
                    context_window = "Context unavailable"
                
                # Rule 1: print()
                if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'print':
                    issue_data = {
                        "line": node.lineno, "category": "Style", "severity": "Low",
                        "issue": "Avoid print(). Use logging instead.",
                        "snippet": context_window
                    }

                # Rule 2: == None
                elif isinstance(node, ast.Compare):
                    for op in node.ops:
                        if isinstance(op, ast.Eq):
                            for comp in node.comparators:
                                if isinstance(comp, ast.Constant) and comp.value is None:
                                    issue_data = {
                                        "line": node.lineno, "category": "Logic", "severity": "Medium",
                                        "issue": "Use 'is None' for identity checks.",
                                        "snippet": context_window
                                    }
                
                # Rule 3: eval()
                elif isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'eval':
                    issue_data = {
                        "line": node.lineno, "category": "Security", "severity": "High",
                        "issue": "Security Risk: 'eval()' detected.",
                        "snippet": context_window
                    }
                
                # Rule 4: Arg count
                elif isinstance(node, ast.FunctionDef):
                    arg_count = len(node.args.args)
                    if arg_count > 5:
                        issue_data = {
                            "line": node.lineno, "category": "Complexity", "severity": "Medium",
                            "issue": f"Function '{node.name}' has too many arguments ({arg_count}).",
                            "snippet": context_window
                        }

                # Rule 5: Mutable Default Arguments
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict)):
                            file_issues.append({
                                "line": node.lineno, "category": "Security", "severity": "High",
                                "issue": f"Dangerous mutable default argument in '{node.name}'.",
                                "snippet": context_window
                            })

                # Rule 6: Bare Except blocks
                elif isinstance(node, ast.ExceptHandler) and node.type is None:
                    issue_data = {
                        "line": node.lineno, "category": "Error Handling", "severity": "Medium",
                        "issue": "Bare 'except:' caught. Specify an exception type.",
                        "snippet": context_window
                    }
                
                # Rule 7: Recursion
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name
                    for sub_node in ast.walk(node):
                        if isinstance(sub_node, ast.Call) and getattr(sub_node.func, 'id', None) == func_name:
                            sub_line = sub_node.lineno
                            sub_start = max(0, sub_line - 5)
                            sub_end = min(len(lines), sub_line + 5)
                            recursion_context = "\n".join(lines[sub_start:sub_end])
                            file_issues.append({
                                "line": sub_line,
                                "category": "Logic",
                                "severity": "High",
                                "issue": f"Structural Recursion detected in '{func_name}'.",
                                "snippet": recursion_context
                            })
                            break
                if issue_data:
                    file_issues.append(issue_data)
            
        except SyntaxError:
            # --- FALLBACK: REGEX (Structured as dictionaries for the Reporter) ---
            fallback_snippet = "\n".join(clean_code.split('\n')[:15])
            if "print(" in clean_code:
                file_issues.append({
                    "line": "N/A", "category": "Style", "severity": "Low",
                    "issue": "Found print() statement. Avoid print().",
                    "snippet": fallback_snippet, 
                    "suggestion": "Use logging"
                })
            if "== None" in clean_code:
                file_issues.append({
                    "line": "N/A", "category": "Logic", "severity": "Medium",
                    "issue": "Found '== None'. Use 'is None' for identity checks.",
                    "snippet": fallback_snippet, 
                    "suggestion": "Use 'is None'"
                })
            if "eval(" in clean_code:
                file_issues.append({
                    "line": "N/A", "category": "Security", "severity": "High",
                    "issue": "Security Risk: 'eval()' detected.",
                    "snippet": fallback_snippet, 
                    "suggestion": "Remove eval() for safety"
                })
            
            # Re-adding the "Too many arguments" regex check
            if re.search(r"def\s+\w+\(.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\s*,\s*.*\)", clean_code):
                 file_issues.append({
                    "line": "N/A", "category": "Complexity", "severity": "Medium",
                    "issue": "Function has too many arguments (Detected via Regex).",
                    "snippet": fallback_snippet, 
                    "suggestion": "Refactor into a class or dictionary"
                })

        # --- LEVEL 2: SEMANTIC ANALYSIS (CODEBERT) ---
        if self.use_ai and self.nlp_engine:
            try:
                if len(clean_code.strip()) > 15:
                    ai_insights = self.nlp_engine.analyze(clean_code)
                    for insight in ai_insights:
                        file_issues.append({
                            "line": "N/A", 
                            "category": "AI Insight", 
                            "severity": "Info",
                            "issue": insight, 
                            "snippet": clean_code[:500], 
                            "suggestion": "Review suggested changes"
                        })
            except Exception as e:
                print(f"DEBUG: Local AI Engine error: {e}")
                            
        # --- LEVEL 3: THE UNIFIED LLAMA3 ARCHITECT REVIEW ---
        if self.use_ai and self.nlp_engine and file_issues:
            try:
                # 1. Cleaner Summary for Llama (Reduce tokens for speed)
                summary_for_ai = ""
                for idx, i in enumerate(file_issues):
                    # Only give Llama a snippet if it's small, otherwise it gets slow
                    trunc_snippet = str(i.get('snippet', ''))[:150].replace('\n', ' ')
                    summary_for_ai += f"ID:{idx} | Issue: {i.get('issue')} | Code: {trunc_snippet}\n"

                # 2. Call local Llama
                batch_fixes = self.nlp_engine.get_batch_refactor(
                    filename=filename,
                    issues_summary=summary_for_ai,
                    project_context=project_context
                )

                # 3. Map the { "fix": "...", "insight": "..." } structure back
                for idx, issue in enumerate(file_issues):
                    res = batch_fixes.get(f"ID{idx}") or batch_fixes.get(str(idx))
                    if isinstance(res, dict):
                        fix = res.get('fix', 'No code fix provided.')
                        insight = res.get('insight', 'No detailed insight.')
                        issue["suggestion"] = f"**Fix:** `{fix}`\n\n**Insight:** {insight}"
                    else:
                        issue["suggestion"] = "Llama-3 could not generate a surgical fix for this specific issue."
        
            except Exception as e:
                print(f"Llama-3 Refactor failed: {e}")
                for issue in file_issues:
                    if "suggestion" not in issue:
                        issue["suggestion"] = "Local AI refactor skipped due to error."
                    
        return file_issues
    
    def analyze_architecture(self, project_tree, project_context):
        if not self.use_ai or self.nlp_engine is None:
            return "Architecture analysis requires AI to be enabled (use_ai=True)."
        return self.nlp_engine.get_architecture_review(project_tree, project_context)