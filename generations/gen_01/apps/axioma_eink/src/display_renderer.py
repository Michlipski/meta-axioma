"""Pure Static Zero-JavaScript Electrophoretic Display Renderer for Axioma E-Ink.

Adheres strictly to hardware constraints for e-paper / Kindle / Kobo web browsers:
1. Zero JavaScript (no <script> tags, no DOM scripting) preventing low-RAM crashes.
2. 15-Minute HTTP meta-refresh (<meta http-equiv="refresh" content="900">).
3. Zero CSS transitions, keyframes, or animations to avoid electrophoretic screen flashing.
4. 1-bit high-contrast black/white typography with glanceable legibility.
"""

from __future__ import annotations

import html
import time
from typing import List

from models import EinkBoardState, TaskItem, TaskStatus


def render_display_html(state: EinkBoardState) -> str:
    """Renders high-contrast zero-JS HTML for electrophoretic ambient glanceboards."""
    now_str = time.strftime("%A, %b %d • %H:%M", time.localtime(state.sync_timestamp))
    total = state.total_focus_tasks
    done = state.completed_count
    pending = total - done

    # Generate progress bar blocks
    progress_blocks = ""
    for i in range(total):
        if i < done:
            progress_blocks += "■ "
        else:
            progress_blocks += "□ "
    progress_blocks = progress_blocks.strip()

    # Build tasks markup
    tasks_html = []
    if not state.tasks:
        tasks_html.append("""
        <div class="empty-state">
            <p class="empty-title">NO ACTIVE FOCUS TASKS</p>
            <p class="empty-sub">Capture 3 to 5 priorities from your phone or laptop to populate your ambient board.</p>
        </div>
        """)
    else:
        for idx, task in enumerate(state.tasks, start=1):
            is_done = task.status == TaskStatus.DONE
            box_class = "task-row is-done" if is_done else "task-row"
            check_box = "■" if is_done else "□"
            title_escaped = html.escape(task.title)
            tag_escaped = html.escape(task.tag)

            tasks_html.append(f"""
            <div class="{box_class}">
                <div class="task-col-num">{idx}</div>
                <div class="task-col-check">{check_box}</div>
                <div class="task-col-content">
                    <span class="task-title">{title_escaped}</span>
                    <span class="task-tag">{tag_escaped}</span>
                </div>
            </div>
            """)

    rendered_tasks = "\n".join(tasks_html)
    quote_escaped = html.escape(state.quote_of_the_day)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <!-- Automated 15-Minute Electrophoretic Ambient Meta-Refresh -->
    <meta http-equiv="refresh" content="900">
    <title>Axioma E-Ink • Ambient Focus</title>
    <style>
        /* Strict Electrophoretic Constraints: Zero Animations, High Contrast 1-Bit Palette */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
        }}
        html, body {{
            background-color: #ffffff;
            color: #000000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, serif;
            font-size: 18px;
            line-height: 1.35;
            width: 100%;
            min-height: 100vh;
        }}
        body {{
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .header {{
            border-bottom: 4px solid #000000;
            padding-bottom: 14px;
            margin-bottom: 20px;
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 6px;
        }}
        .time-label {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .status-badge {{
            font-size: 15px;
            font-weight: 700;
            border: 2px solid #000000;
            padding: 2px 8px;
            text-transform: uppercase;
        }}
        .board-title {{
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -1px;
            text-transform: uppercase;
            margin-top: 4px;
        }}
        .progress-bar-container {{
            margin-top: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 15px;
            font-weight: 700;
        }}
        .progress-glyphs {{
            font-size: 18px;
            letter-spacing: 2px;
        }}

        /* Tasks Container */
        .tasks-container {{
            flex-grow: 1;
            margin-bottom: 24px;
        }}
        .task-row {{
            display: flex;
            align-items: flex-start;
            padding: 16px 0;
            border-bottom: 2px solid #000000;
        }}
        .task-row:last-child {{
            border-bottom: 3px solid #000000;
        }}
        .task-col-num {{
            font-size: 26px;
            font-weight: 900;
            min-width: 38px;
            line-height: 1;
            padding-top: 2px;
        }}
        .task-col-check {{
            font-size: 28px;
            line-height: 0.9;
            min-width: 36px;
            margin-right: 12px;
            font-weight: 900;
        }}
        .task-col-content {{
            flex-grow: 1;
        }}
        .task-title {{
            display: block;
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.3px;
            word-break: break-word;
        }}
        .task-tag {{
            display: inline-block;
            margin-top: 6px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            border: 1px solid #000000;
            padding: 1px 6px;
        }}
        .task-row.is-done .task-title {{
            text-decoration: line-through;
            opacity: 0.55;
            font-weight: 600;
        }}
        .task-row.is-done .task-tag {{
            opacity: 0.55;
        }}

        /* Empty State */
        .empty-state {{
            padding: 60px 0;
            text-align: center;
            border: 2px dashed #000000;
            margin: 20px 0;
        }}
        .empty-title {{
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 8px;
        }}
        .empty-sub {{
            font-size: 15px;
            max-width: 400px;
            margin: 0 auto;
        }}

        /* Footer */
        .footer {{
            border-top: 2px solid #000000;
            padding-top: 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .quote {{
            font-size: 14px;
            font-style: italic;
            font-weight: 600;
        }}
        .meta-line {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-top">
            <span class="time-label">{now_str}</span>
            <span class="status-badge">{done} / {total} DONE</span>
        </div>
        <h1 class="board-title">{html.escape(state.board_title)}</h1>
        <div class="progress-bar-container">
            <span class="progress-glyphs">{progress_blocks}</span>
            <span>{pending} FOCUS REMAINING</span>
        </div>
    </header>

    <main class="tasks-container">
{rendered_tasks}
    </main>

    <footer class="footer">
        <div class="quote">“{quote_escaped}”</div>
        <div class="meta-line">
            <span>AXIOMA E-INK ROUTER • 15M REFRESH</span>
            <span>PORT 8096</span>
        </div>
    </footer>
</body>
</html>
"""
