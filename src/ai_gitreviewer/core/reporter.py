import time
import os
import html
import re
import markdown


class HTMLReporter:
    def __init__(self, results, arch_feedback=None, output_file="review_report.html"):
        self.results = results
        self.arch_feedback = arch_feedback
        self.output_file = output_file

    def _parse_suggestion(self, suggestion_data):
        if isinstance(suggestion_data, dict):
            return (
                suggestion_data.get('fix', 'Manual review required.'),
                suggestion_data.get('insight', 'Ensures code aligns with production standards.')
            )
        if isinstance(suggestion_data, str):
            fix_match     = re.search(r'\*\*Fix:\*\*\s*`?(.*?)`?(?:\n\n|\Z)', suggestion_data, re.DOTALL)
            insight_match = re.search(r'\*\*Insight:\*\*\s*(.*?)(?:\Z)', suggestion_data, re.DOTALL)
            fix     = fix_match.group(1).strip()     if fix_match     else suggestion_data.strip()
            insight = insight_match.group(1).strip() if insight_match else "Detected via structural analysis."
            return fix, insight
        return "Manual review recommended.", "Detected via structural/regex rules."

    def _severity_rank(self, s):
        return {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}.get(s.lower(), 0)

    def _file_risk_score(self, issues):
        weights = {"Critical": 8, "High": 3, "Medium": 2, "Low": 1, "Info": 0}
        return sum(weights.get(i.get("severity", "Low"), 1) for i in issues)

    def _severity_config(self, severity):
        configs = {
            'Critical': {'color': '#ff4444', 'bg': 'rgba(220,38,38,0.15)',   'border': 'rgba(220,38,38,0.4)',   'icon': '🔴', 'dot': '#dc2626'},
            'High':     {'color': '#fb923c', 'bg': 'rgba(251,146,60,0.12)',  'border': 'rgba(251,146,60,0.35)', 'icon': '🟠', 'dot': '#f97316'},
            'Medium':   {'color': '#fbbf24', 'bg': 'rgba(251,191,36,0.10)', 'border': 'rgba(251,191,36,0.3)',  'icon': '🟡', 'dot': '#f59e0b'},
            'Low':      {'color': '#60a5fa', 'bg': 'rgba(96,165,250,0.10)', 'border': 'rgba(96,165,250,0.3)',  'icon': '🔵', 'dot': '#3b82f6'},
            'Info':     {'color': '#a78bfa', 'bg': 'rgba(167,139,250,0.10)','border': 'rgba(167,139,250,0.3)', 'icon': '🔮', 'dot': '#8b5cf6'},
        }
        return configs.get(severity, configs['Low'])

    def _category_config(self, category):
        configs = {
            'Security':       {'color': '#fca5a5', 'bg': 'rgba(220,38,38,0.15)'},
            'Logic':          {'color': '#fcd34d', 'bg': 'rgba(217,119,6,0.15)'},
            'Complexity':     {'color': '#c4b5fd', 'bg': 'rgba(124,58,237,0.15)'},
            'Error Handling': {'color': '#67e8f9', 'bg': 'rgba(8,145,178,0.15)'},
            'Style':          {'color': '#93c5fd', 'bg': 'rgba(37,99,235,0.15)'},
            'Performance':    {'color': '#6ee7b7', 'bg': 'rgba(5,150,105,0.15)'},
            'AI Insight':     {'color': '#86efac', 'bg': 'rgba(22,163,74,0.15)'},
        }
        return configs.get(category, {'color': '#94a3b8', 'bg': 'rgba(71,85,105,0.2)'})

    def _highlight_fix(self, fix_code, snippet):
        snippet_lines = set(l.strip() for l in snippet.splitlines() if l.strip())
        result_parts  = []
        for line in fix_code.splitlines():
            stripped = line.strip()
            is_new   = stripped and stripped not in snippet_lines
            escaped  = html.escape(line)
            if is_new:
                result_parts.append(
                    f'<span style="display:block;background:rgba(74,222,128,0.12);'
                    f'border-left:3px solid #4ade80;padding-left:6px;'
                    f'color:#4ade80;font-weight:500">{escaped}</span>'
                )
            else:
                result_parts.append(
                    f'<span style="display:block;color:#64748b;padding-left:9px">{escaped}</span>'
                )
        return "\n".join(result_parts)

    def generate(self):
        all_issues   = [i for issues in self.results.values() for i in issues]
        total_issues = len(all_issues)
        critical_sev = sum(1 for i in all_issues if i.get('severity') == 'Critical')
        high_sev     = sum(1 for i in all_issues if i.get('severity') == 'High')
        med_sev      = sum(1 for i in all_issues if i.get('severity') == 'Medium')
        low_sev      = sum(1 for i in all_issues if i.get('severity') == 'Low')
        files_count  = len(self.results)

        cat_counts: dict[str, int] = {}
        for i in all_issues:
            c = i.get('category', 'General')
            cat_counts[c] = cat_counts.get(c, 0) + 1

        sorted_files = sorted(
            self.results.items(),
            key=lambda kv: self._file_risk_score(kv[1]),
            reverse=True
        )

        css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0f1e;
            color: #e2e8f0;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a5f 100%);
            padding: 36px 0 28px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            margin-bottom: 28px;
        }
        .header-inner { max-width: 1240px; margin: auto; padding: 0 28px; }
        .header-badge {
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(139,92,246,0.18); border: 1px solid rgba(139,92,246,0.4);
            color: #a78bfa; font-size: 0.7em; font-weight: 700;
            padding: 4px 14px; border-radius: 20px;
            text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 14px;
        }
        .header h1 { font-size: 2.1em; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em; margin-bottom: 4px; }
        .header h1 span { color: #818cf8; }
        .timestamp { color: #475569; font-size: 0.8em; margin-top: 6px; }

        .container { max-width: 1240px; margin: auto; padding: 0 28px 80px; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #131929; border: 1px solid #1e2d45;
            border-radius: 12px; padding: 16px 12px;
            text-align: center; position: relative; overflow: hidden;
            transition: transform 0.18s, border-color 0.18s, box-shadow 0.18s;
            cursor: default;
        }
        .stat-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0;
            height: 3px; background: var(--accent);
        }
        .stat-card:hover { transform: translateY(-3px); border-color: var(--accent); }
        .stat-card.clickable { cursor: pointer; }
        .stat-card.clickable:hover { box-shadow: 0 0 0 1px var(--accent), 0 8px 24px rgba(0,0,0,0.4); }
        .stat-card.active-filter {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent), 0 8px 28px rgba(0,0,0,0.5);
            transform: translateY(-3px);
        }
        .stat-card.active-filter::after {
            content: '▼ filtered';
            position: absolute;
            bottom: 6px; left: 0; right: 0;
            text-align: center;
            font-size: 0.55em; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.08em;
            color: var(--accent); opacity: 0.8;
        }
        .stat-icon  { font-size: 1.3em; margin-bottom: 6px; display: block; }
        .stat-label { display: block; color: #475569; font-size: 0.65em; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 700; margin-bottom: 5px; }
        .stat-value { font-size: 1.9em; font-weight: 800; display: block; color: var(--accent); line-height: 1; }

        .category-strip {
            display: flex; flex-wrap: wrap; gap: 8px;
            margin-bottom: 28px; align-items: center;
        }
        .category-strip-label { color: #475569; font-size: 0.72em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-right: 4px; }
        .cat-pill {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 0.75em; font-weight: 600;
            padding: 4px 12px; border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .cat-pill-count {
            background: rgba(255,255,255,0.12);
            border-radius: 10px; padding: 0 6px;
            font-weight: 700; font-size: 0.9em;
        }

        .filter-bar {
            position: sticky; top: 0; z-index: 100;
            background: rgba(10,15,30,0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #1e2d45;
            padding: 10px 0;
            margin: 0 -28px 28px;
            padding-left: 28px;
        }
        .filter-tabs { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
        .filter-label { color: #475569; font-size: 0.7em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; margin-right: 6px; }
        .filter-tab {
            display: inline-flex; align-items: center; gap: 5px;
            padding: 5px 14px; border-radius: 20px;
            border: 1px solid #1e2d45;
            background: #131929; color: #64748b;
            font-size: 0.75em; font-weight: 600;
            cursor: pointer; transition: all 0.16s;
            user-select: none;
        }
        .filter-tab:hover { border-color: #334155; color: #94a3b8; }
        .filter-tab.active { background: #1e3a5f; border-color: #3b82f6; color: #93c5fd; }
        .filter-tab.active.sev-critical { background: rgba(220,38,38,0.15); border-color: #dc2626; color: #fca5a5; }
        .filter-tab.active.sev-high     { background: rgba(251,146,60,0.15); border-color: #f97316; color: #fed7aa; }
        .filter-tab.active.sev-medium   { background: rgba(251,191,36,0.12); border-color: #f59e0b; color: #fde68a; }
        .filter-tab.active.sev-low      { background: rgba(96,165,250,0.12); border-color: #3b82f6; color: #bfdbfe; }
        .tab-count { font-size: 0.9em; opacity: 0.8; }

        .section-label { font-size: 0.7em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #334155; margin-bottom: 12px; padding-left: 2px; }

        .arch-card {
            background: #131929; border: 1px solid #1e2d45;
            border-radius: 14px; overflow: hidden; margin-bottom: 28px;
            box-shadow: 0 4px 32px rgba(0,0,0,0.4);
        }
        .arch-header {
            background: linear-gradient(90deg, #1e1b4b, #1e3a5f);
            padding: 13px 20px; display: flex; align-items: center; gap: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }
        .arch-header-title { font-size: 0.82em; font-weight: 700; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.08em; }
        .arch-body { padding: 22px 24px; color: #94a3b8; font-size: 0.91em; line-height: 1.8; }
        .arch-body h1, .arch-body h2, .arch-body h3 { color: #a5b4fc; margin: 16px 0 8px; font-size: 1em; font-weight: 700; }
        .arch-body p  { margin-bottom: 10px; }
        .arch-body strong { color: #e2e8f0; }
        .arch-body ul { padding-left: 20px; margin-bottom: 10px; }
        .arch-body li { margin-bottom: 4px; }
        .arch-note {
            margin: 0 20px 20px; padding: 11px 16px;
            background: rgba(99,102,241,0.07); border: 1px solid rgba(99,102,241,0.18);
            border-radius: 8px; font-size: 0.81em; color: #6366f1;
        }

        .file-card {
            background: #131929; border: 1px solid #1e2d45;
            border-radius: 14px; overflow: hidden; margin-bottom: 20px;
            box-shadow: 0 4px 28px rgba(0,0,0,0.35);
            transition: border-color 0.2s;
        }
        .file-card:hover { border-color: #334155; }
        .file-header {
            background: #0d1424; padding: 11px 18px;
            display: flex; align-items: center; gap: 10px;
            border-bottom: 1px solid #1e2d45;
        }
        .file-name { font-family: 'Fira Code', monospace; font-size: 0.86em; color: #4ade80; font-weight: 500; flex: 1; }
        .risk-score {
            display: inline-flex; align-items: center; gap: 5px;
            font-size: 0.7em; font-weight: 700;
            padding: 3px 10px; border-radius: 20px;
            background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25);
            color: #f87171;
        }
        .risk-score.low-risk { background: rgba(96,165,250,0.1); border-color: rgba(96,165,250,0.25); color: #60a5fa; }
        .risk-score.med-risk { background: rgba(251,191,36,0.1); border-color: rgba(251,191,36,0.25); color: #fbbf24; }
        .file-count { background: #1e2d45; color: #64748b; font-size: 0.7em; font-weight: 600; padding: 2px 10px; border-radius: 20px; white-space: nowrap; }

        .issue-row {
            border-bottom: 1px solid #0f1929;
            position: relative;
        }
        .issue-row:last-child { border-bottom: none; }
        .issue-row[data-hidden="true"] { display: none; }

        .issue-header {
            padding: 16px 18px 0;
            cursor: pointer;
            display: flex; flex-direction: column; gap: 8px;
        }
        .issue-header:hover { background: rgba(255,255,255,0.01); }

        .issue-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .line-badge {
            background: #1e2d45; color: #475569;
            font-family: 'Fira Code', monospace; font-size: 0.7em;
            padding: 3px 10px; border-radius: 6px; font-weight: 500;
        }
        .severity-badge {
            display: inline-flex; align-items: center; gap: 4px;
            font-size: 0.7em; font-weight: 700;
            padding: 3px 10px; border-radius: 20px;
            text-transform: uppercase; letter-spacing: 0.06em;
        }
        .category-badge { font-size: 0.7em; font-weight: 600; padding: 3px 10px; border-radius: 6px; }
        .collapse-arrow { margin-left: auto; color: #334155; font-size: 0.85em; transition: transform 0.2s; flex-shrink: 0; }
        .issue-row.collapsed .collapse-arrow { transform: rotate(-90deg); }

        .issue-title { font-size: 0.95em; font-weight: 600; color: #f1f5f9; line-height: 1.4; padding: 0 18px 14px; }

        .issue-body { padding: 0 18px 18px; }
        .issue-row.collapsed .issue-body { display: none; }

        .panels { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
        @media (max-width: 800px) { .panels { grid-template-columns: 1fr; } }

        .panel { border-radius: 10px; overflow: hidden; }
        .panel-header {
            padding: 8px 12px; font-size: 0.68em; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.08em;
            display: flex; align-items: center; gap: 6px;
        }
        .panel-snippet .panel-header { background: #1a1020; color: #f87171; border-bottom: 1px solid #2d1b1b; }
        .panel-fix     .panel-header { background: #0d2010; color: #4ade80; border-bottom: 1px solid #1a3020; }

        .copy-btn {
            margin-left: auto; background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1); color: #64748b;
            font-size: 0.8em; padding: 2px 9px; border-radius: 5px;
            cursor: pointer; transition: all 0.15s; font-family: inherit;
        }
        .copy-btn:hover { background: rgba(255,255,255,0.12); color: #94a3b8; }
        .copy-btn.copied { color: #4ade80; border-color: #4ade80; }

        .panel-code {
            background: #080e1a; color: #8899aa;
            padding: 14px; font-family: 'Fira Code', monospace;
            font-size: 0.81em; line-height: 1.65;
            overflow-x: auto; white-space: pre-wrap; word-break: break-word;
            min-height: 80px;
        }

        .insight-box {
            background: rgba(79,70,229,0.06); border: 1px solid rgba(79,70,229,0.14);
            border-radius: 8px; padding: 11px 15px;
            font-size: 0.83em; color: #64748b; line-height: 1.6;
        }
        .insight-box strong { color: #6366f1; }

        .empty-filter {
            display: none; text-align: center; padding: 40px 20px;
            color: #334155; font-size: 0.9em;
        }

        .footer { text-align: center; padding: 32px 0 16px; color: #1e2d45; font-size: 0.78em; }
        .footer a { color: #3730a3; text-decoration: none; }
        .footer a:hover { color: #6366f1; }
        """

        js = """
        function setFilter(sev, scroll) {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            const tab = document.querySelector('.filter-tab[data-sev="' + sev + '"]');
            if (tab) tab.classList.add('active');

            document.querySelectorAll('.stat-card.clickable').forEach(c => c.classList.remove('active-filter'));
            if (sev !== 'all') {
                const card = document.querySelector('.stat-card[data-sev="' + sev + '"]');
                if (card) card.classList.add('active-filter');
            }

            const rows = document.querySelectorAll('.issue-row');
            let visible = 0;
            rows.forEach(row => {
                const match = sev === 'all' || row.dataset.severity === sev;
                row.dataset.hidden = match ? 'false' : 'true';
                if (match) visible++;
            });

            document.querySelectorAll('.file-card').forEach(card => {
                const hasVisible = Array.from(card.querySelectorAll('.issue-row'))
                    .some(r => r.dataset.hidden !== 'true');
                card.style.display = hasVisible ? '' : 'none';
            });

            const empty = document.getElementById('empty-filter');
            empty.style.display = visible === 0 ? 'block' : 'none';

            if (scroll) {
                const findings = document.getElementById('findings-section');
                if (findings) {
                    setTimeout(() => findings.scrollIntoView({ behavior: 'smooth', block: 'start' }), 60);
                }
            }
        }

        function toggleIssue(el) {
            const row = el.closest('.issue-row');
            row.classList.toggle('collapsed');
        }

        function copyCode(btn) {
            const code = btn.closest('.panel').querySelector('.panel-code');
            const text = code.innerText;
            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = '✓ Copied';
                btn.classList.add('copied');
                setTimeout(() => { btn.textContent = '⎘ Copy'; btn.classList.remove('copied'); }, 2000);
            });
        }

        document.addEventListener('DOMContentLoaded', () => setFilter('all'));
        """

        doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Code Review Report</title>
  <style>{css}</style>
</head>
<body>

<div class="header">
  <div class="header-inner">
    <div class="header-badge">⚡ CodeBERT + Llama-3 via Groq</div>
    <h1>🧠 AI Code Review <span>Dashboard</span></h1>
    <div class="timestamp">Generated on {time.strftime('%A, %B %d %Y at %H:%M:%S')}</div>
  </div>
</div>

<div class="container">
"""

        doc += f"""
  <div class="section-label">📊 Scan Summary</div>
  <div class="stats-grid">
    <div class="stat-card" style="--accent:#64748b">
      <span class="stat-icon">📁</span>
      <span class="stat-label">Files</span>
      <span class="stat-value">{files_count}</span>
    </div>
    <div class="stat-card clickable" data-sev="Critical" style="--accent:#dc2626" onclick="setFilter('Critical', true)">
      <span class="stat-icon">🔴</span>
      <span class="stat-label">Critical</span>
      <span class="stat-value">{critical_sev}</span>
    </div>
    <div class="stat-card clickable" data-sev="High" style="--accent:#f97316" onclick="setFilter('High', true)">
      <span class="stat-icon">🟠</span>
      <span class="stat-label">High</span>
      <span class="stat-value">{high_sev}</span>
    </div>
    <div class="stat-card clickable" data-sev="Medium" style="--accent:#f59e0b" onclick="setFilter('Medium', true)">
      <span class="stat-icon">🟡</span>
      <span class="stat-label">Medium</span>
      <span class="stat-value">{med_sev}</span>
    </div>
    <div class="stat-card clickable" data-sev="Low" style="--accent:#3b82f6" onclick="setFilter('Low', true)">
      <span class="stat-icon">🔵</span>
      <span class="stat-label">Low</span>
      <span class="stat-value">{low_sev}</span>
    </div>
    <div class="stat-card" style="--accent:#4ade80">
      <span class="stat-icon">📋</span>
      <span class="stat-label">Total</span>
      <span class="stat-value">{total_issues}</span>
    </div>
  </div>
"""

        if cat_counts:
            doc += '  <div class="category-strip">\n'
            doc += '    <span class="category-strip-label">By category:</span>\n'
            for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
                cfg = self._category_config(cat)
                doc += (
                    f'    <span class="cat-pill" style="color:{cfg["color"]};background:{cfg["bg"]}">'
                    f'{html.escape(cat)} <span class="cat-pill-count">{cnt}</span></span>\n'
                )
            doc += '  </div>\n'

        doc += f"""
  <div class="filter-bar">
    <div class="filter-tabs">
      <span class="filter-label">Filter:</span>
      <span class="filter-tab active" data-sev="all" onclick="setFilter('all')">All <span class="tab-count">{total_issues}</span></span>
"""
        if critical_sev:
            doc += f'      <span class="filter-tab sev-critical" data-sev="Critical" onclick="setFilter(\'Critical\')">🔴 Critical <span class="tab-count">{critical_sev}</span></span>\n'
        if high_sev:
            doc += f'      <span class="filter-tab sev-high" data-sev="High" onclick="setFilter(\'High\')">🟠 High <span class="tab-count">{high_sev}</span></span>\n'
        if med_sev:
            doc += f'      <span class="filter-tab sev-medium" data-sev="Medium" onclick="setFilter(\'Medium\')">🟡 Medium <span class="tab-count">{med_sev}</span></span>\n'
        if low_sev:
            doc += f'      <span class="filter-tab sev-low" data-sev="Low" onclick="setFilter(\'Low\')">🔵 Low <span class="tab-count">{low_sev}</span></span>\n'
        doc += "    </div>\n  </div>\n"

        if self.arch_feedback:
            try:
                arch_html = markdown.markdown(self.arch_feedback)
            except Exception:
                arch_html = self.arch_feedback.replace('\n', '<br>')

            doc += f"""
  <div class="section-label">🏗️ Architectural Analysis</div>
  <div class="arch-card">
    <div class="arch-header">
      <span>🏗️</span>
      <span class="arch-header-title">Project Architecture Critique — Llama-3 Senior Architect Review</span>
    </div>
    <div class="arch-body">{arch_html}</div>
    <div class="arch-note">
      💡 <strong>Scope:</strong> This analysis considers your entire project tree to identify structural gaps, scalability bottlenecks, and missing best-practice patterns.
    </div>
  </div>
"""

        if sorted_files:
            doc += '  <div id="findings-section" class="section-label">🔍 File-by-File Findings — sorted by risk score</div>\n'

        for file_path, issues in sorted_files:
            risk  = self._file_risk_score(issues)
            count = len(issues)

            if risk >= 6:
                risk_class, risk_label = "high-risk", f"⚠ Risk {risk}"
            elif risk >= 3:
                risk_class, risk_label = "med-risk",  f"▲ Risk {risk}"
            else:
                risk_class, risk_label = "low-risk",  f"✓ Risk {risk}"

            doc += f"""
  <div class="file-card">
    <div class="file-header">
      <span style="color:#4ade80;font-size:0.9em">📄</span>
      <span class="file-name">{html.escape(str(file_path))}</span>
      <span class="risk-score {risk_class}">{risk_label}</span>
      <span class="file-count">{count} issue{'s' if count != 1 else ''}</span>
    </div>
"""
            for idx, issue in enumerate(issues):
                severity = issue.get('severity', 'Low')
                category = issue.get('category', 'General')
                line     = issue.get('line', 'N/A')
                title    = html.escape(str(issue.get('issue', 'Structural Issue')))
                snippet  = str(issue.get('snippet', 'N/A'))
                fix_raw, insight = self._parse_suggestion(issue.get('suggestion', ''))
                insight         = html.escape(str(insight))

                sev_cfg = self._severity_config(severity)
                cat_cfg = self._category_config(category)

                highlighted_fix = self._highlight_fix(fix_raw, snippet)
                snippet_escaped = html.escape(snippet)

                doc += f"""
    <div class="issue-row" data-severity="{html.escape(severity)}" data-hidden="false">
      <div class="issue-header" onclick="toggleIssue(this)">
        <div class="issue-meta">
          <span class="line-badge">Line {line}</span>
          <span class="severity-badge" style="color:{sev_cfg['color']};background:{sev_cfg['bg']};border:1px solid {sev_cfg['border']}">
            {sev_cfg['icon']} {html.escape(severity)}
          </span>
          <span class="category-badge" style="color:{cat_cfg['color']};background:{cat_cfg['bg']}">
            {html.escape(category)}
          </span>
          <span class="collapse-arrow">▼</span>
        </div>
      </div>
      <div class="issue-title">{title}</div>
      <div class="issue-body">
        <div class="panels">
          <div class="panel panel-snippet">
            <div class="panel-header">
              ❌ Current Code
              <button class="copy-btn" onclick="copyCode(this)">⎘ Copy</button>
            </div>
            <div class="panel-code">{snippet_escaped}</div>
          </div>
          <div class="panel panel-fix">
            <div class="panel-header">
              ✅ AI Suggested Fix
              <button class="copy-btn" onclick="copyCode(this)">⎘ Copy</button>
            </div>
            <div class="panel-code">{highlighted_fix}</div>
          </div>
        </div>
        <div class="insight-box">
          <strong>💡 Production Insight:</strong> {insight}
        </div>
      </div>
    </div>
"""
            doc += "  </div>\n"

        doc += '  <div class="empty-filter" id="empty-filter">No issues match the selected filter.</div>\n'

        doc += f"""
  <div class="footer">
    Generated by <a href="https://github.com/ashg2099/ai-git-Reviewer">AI-GitReviewer</a> &nbsp;·&nbsp;
    Powered by CodeBERT + Llama-3 via Groq &nbsp;·&nbsp;
    {time.strftime('%Y')}
  </div>
</div>

<script>{js}</script>
</body>
</html>"""

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(doc)