import time
import os
import html
import markdown
import re

class HTMLReporter:
    def __init__(self, results, arch_feedback=None, output_file="review_report.html"):
        self.results = results
        self.arch_feedback = arch_feedback
        self.output_file = output_file

    def _simple_markdown(self, text):
        """Minimal markdown parser for bold, code blocks, and line breaks."""
        if not text: return ""
        # Convert Bold **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Convert Inline Code `code`
        text = re.sub(r'`([^`]+)`', r'<code style="background:#eee;padding:2px 4px;border-radius:3px;">\1</code>', text)
        # Convert Newlines
        text = text.replace('\n', '<br>')
        return text
    
    def generate(self):
        css = """
        body { font-family: 'Inter', -apple-system, sans-serif; background: #f4f7f6; color: #333; margin: 20px; }
        .container { max-width: 1200px; margin: auto; }
        
        h1 { color: #1a202c; padding-bottom: 10px; margin-bottom: 5px; }
        .timestamp { color: #718096; font-size: 0.9em; margin-bottom: 25px; }
        
        /* Stats Dashboard */
        .stats-dashboard { display: flex; flex-wrap: nowrap; gap: 12px; margin-bottom: 30px; width: 100%; }
        .stat-card { 
            flex: 1; background: white; padding: 15px 10px; border-radius: 8px; 
            text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }
        .stat-label { display: block; color: #64748b; font-size: 0.7em; text-transform: uppercase; font-weight: 700; margin-bottom: 4px; }
        .stat-value { font-size: 1.4em; font-weight: 800; display: block; }

        /* NEW: Architecture Section Styling */
        .arch-section {
            background: #ffffff;
            border-left: 6px solid #6c5ce7;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            line-height: 1.6;
        }
        .arch-section h2 { margin-top: 0; color: #6c5ce7; font-size: 1.2em; display: flex; align-items: center; }
        .arch-content { font-size: 0.95em; color: #2d3748; white-space: pre-wrap; }

        .file-section { 
            margin-bottom: 30px; border: 1px solid #e2e8f0; border-radius: 8px; 
            overflow: hidden; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .file-header { background: #2d3748; color: #edf2f7; padding: 12px 20px; font-family: 'Fira Code', monospace; font-size: 0.9em; }
        
        table { width: 100%; border-collapse: collapse; }
        th { background: #edf2f7; text-align: left; padding: 12px; font-weight: 600; text-transform: uppercase; font-size: 0.75em; border-bottom: 2px solid #e2e8f0; color: #4a5568; }
        td { padding: 15px 12px; vertical-align: top; border-bottom: 1px solid #edf2f7; }
        
        .severity-High { color: #e53e3e; font-weight: bold; }
        .severity-Medium { color: #dd6b20; font-weight: bold; }
        .severity-Low { color: #3182ce; font-weight: bold; }
        
        .category-tag { background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; color: #4a5568; }
        .issue-text { font-weight: 600; display: block; margin-bottom: 10px; font-size: 1.05em; color: #2d3748; }
        
        .code-block { 
            background: #1e1e1e; color: #d4d4d4; padding: 14px; border-radius: 6px; 
            font-family: 'Fira Code', monospace; font-size: 0.85em; 
            overflow-x: auto; white-space: pre-wrap; margin: 8px 0; border: 1px solid #333;
        }
        .fix-block { border-left: 4px solid #38a169; }
        .ai-label { color: #3182ce; font-weight: bold; font-size: 0.7em; text-transform: uppercase; display: block; margin-top: 15px; }

        .insight-section {
            margin-top: 12px; padding: 12px; background: #f0f7ff;
            border-radius: 6px; font-size: 0.9em; color: #2c5282; border-left: 4px solid #3182ce;
        }
        """

        html_content = f"<html><head><meta charset='UTF-8'><style>{css}</style></head><body><div class='container'>"
        html_content += f"<h1>🚀 AI Code Review Dashboard</h1>"
        html_content += f"<p class='timestamp'>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>"
        
        # --- Stats Logic ---
        all_issues = [issue for issues in self.results.values() for issue in issues]
        total_issues = len(all_issues)
        high_sev = sum(1 for i in all_issues if i.get('severity') == 'High')
        med_sev = sum(1 for i in all_issues if i.get('severity') == 'Medium')
        low_sev = sum(1 for i in all_issues if i.get('severity') == 'Low')

        stats_html = f"""
        <div class="stats-dashboard">
            <div class="stat-card"><span class="stat-label">Files Scanned</span><span class="stat-value">{len(self.results)}</span></div>
            <div class="stat-card" style="border-top: 4px solid #c53030;"><span class="stat-label">High Risk</span><span class="stat-value" style="color: #c53030;">{high_sev}</span></div>
            <div class="stat-card" style="border-top: 4px solid #975a16;"><span class="stat-label">Medium Risk</span><span class="stat-value" style="color: #975a16;">{med_sev}</span></div>
            <div class="stat-card" style="border-top: 4px solid #2b6cb0;"><span class="stat-label">Low Risk</span><span class="stat-value" style="color: #2b6cb0;">{low_sev}</span></div>
            <div class="stat-card" style="border-top: 4px solid #2f855a; background: #f0fff4;"><span class="stat-label">Total Findings</span><span class="stat-value" style="color: #2f855a;">{total_issues}</span></div>
        </div>
        """
        html_content += stats_html

        # --- NEW: Architectural Overview Section ---
        if self.arch_feedback:
            try:
                arch_body = markdown.markdown(self.arch_feedback)
            except ImportError:
                arch_body = self.arch_feedback
                arch_body = re.sub(r'^#+ ', '', arch_body, flags=re.M) # Remove hashtags
                arch_body = arch_body.replace('**', '') # Remove stars
                arch_body = arch_body.replace('\n', '<br>') # Preserve line breaks

            html_content += f"""
            <div class='file-section'>
                <div class='file-header'>🏗️ PROJECT ARCHITECTURE CRITIQUE</div>
                <table>
                    <thead>
                        <tr>
                            <th style='width:5%'>Scope</th>
                            <th style='width:12%'>Category</th>
                            <th style='width:10%'>Status</th>
                            <th>Review Detail</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Project</td>
                            <td><span class='category-tag'>Architecture</span></td>
                            <td><span class='severity-Arch'>Global</span></td>
                            <td>
                                <span class='issue-text'>Structural Evaluation & Scalability Review</span>
                                <span class='ai-label'>📋 Architectural Analysis:</span>
                                <div class='code-block arch-block'>
                                    {arch_body}
                                </div>
                                <div class='insight-section'>
                                    <strong>💡 Architect's Note:</strong> This overview considers the entire project tree to identify structural gaps and scalability bottlenecks.
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """

        # --- File Results ---
        for file_path, issues in self.results.items():
            html_content += f"<div class='file-section'><div class='file-header'>{file_path}</div>"
            html_content += "<table><thead><tr><th style='width:5%'>Line</th><th style='width:12%'>Category</th><th style='width:10%'>Severity</th><th>Review Detail</th></tr></thead><tbody>"
            
            for issue in issues:
                severity = issue.get('severity', 'Low')
                suggestion_data = issue.get('suggestion', "Manual review recommended.")
                
                if isinstance(suggestion_data, dict):
                    fix_code = suggestion_data.get('fix', 'Manual review required.')
                    prod_insight = suggestion_data.get('insight', 'Ensures code aligns with production standards.')
                else:
                    fix_code = suggestion_data
                    prod_insight = "Detected via structural/regex rules."

                html_content += f"""
                <tr>
                    <td>{issue.get('line', 'N/A')}</td>
                    <td><span class='category-tag'>{html.escape(str(issue.get('category', 'General')))}</span></td>
                    <td><span class='severity-{severity}'>{severity}</span></td>
                    <td>
                        <span class='issue-text'>{html.escape(str(issue.get('issue', 'Structural Issue')))}</span>
                        <span class='ai-label'>❌ Current Snippet:</span>
                        <div class='code-block'>{html.escape(str(issue.get('snippet', 'N/A')))}</div>
                        <span class='ai-label'>✨ AI Informed Fix:</span>
                        <div class='code-block fix-block'>{html.escape(str(fix_code))}</div>
                        <div class='insight-section'><strong>💡 Production Insight:</strong> {html.escape(str(prod_insight))}</div>
                    </td>
                </tr>
                """
            html_content += "</tbody></table></div>"
        
        html_content += "</div></body></html>"
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)