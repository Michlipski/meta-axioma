#!/usr/bin/env python3
"""
Bundles the Evolution Dashboard into a standalone, single-file HTML deliverable (`dashboard.html`).
Inlines:
- static/styles.css
- static/app.js
- data/evolution_data.json
- data/philosophy_data.json
- data/g4b_architecture.json
- data/sample_app_simulation.json
Ensures the dashboard can run completely offline, via double-click, file://, or embedded in portfolio.
"""

import json
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = APP_ROOT / "static"
DATA_DIR = APP_ROOT / "data"
OUTPUT_HTML = APP_ROOT / "dashboard.html"
OUTPUT_INDEX = APP_ROOT / "index.html"


def bundle():
    print("Bundling standalone dashboard.html...")

    index_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    styles_css = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
    app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    # Load all data files
    with open(DATA_DIR / "evolution_data.json", encoding="utf-8") as f:
        evolution_data = json.load(f)
    with open(DATA_DIR / "philosophy_data.json", encoding="utf-8") as f:
        philosophy_data = json.load(f)
    with open(DATA_DIR / "g4b_architecture.json", encoding="utf-8") as f:
        g4b_data = json.load(f)
    with open(DATA_DIR / "sample_app_simulation.json", encoding="utf-8") as f:
        simulation_data = json.load(f)

    embedded_payload = {
        "stages": evolution_data.get("stages", []),
        "transformations": evolution_data.get("transformations", []),
        "subsystems": evolution_data.get("subsystems", []),
        "zenith_architecture": evolution_data.get("zenith_architecture", {}),
        "philosophy": philosophy_data,
        "g4b_architecture": g4b_data,
        "sample_app_simulation": simulation_data,
    }

    # Replace <link rel="stylesheet" href="styles.css"> with <style>...</style>
    style_tag = f"<style>\n{styles_css}\n</style>"
    html_out = index_html.replace('<link rel="stylesheet" href="styles.css">', style_tag)

    # Inline KaTeX CSS and JS if present
    katex_vendor = STATIC_DIR / "vendor" / "katex"
    if katex_vendor.is_dir():
        katex_css_file = katex_vendor / "katex.min.css"
        katex_js_file = katex_vendor / "katex.min.js"
        auto_render_js_file = katex_vendor / "auto-render.min.js"

        if katex_css_file.is_file():
            import base64
            import re
            katex_css = katex_css_file.read_text(encoding="utf-8")

            # Inline all WOFF2 fonts as Base64 data URIs for true zero-dependency air-gapped rendering
            fonts_dir = katex_vendor / "fonts"
            if fonts_dir.is_dir():
                def repl_font(m):
                    font_filename = m.group(1)
                    target_file = fonts_dir / font_filename
                    if target_file.is_file():
                        b64 = base64.b64encode(target_file.read_bytes()).decode("ascii")
                        return f'url("data:font/woff2;base64,{b64}")'
                    return m.group(0)

                katex_css = re.sub(r'url\(fonts/(KaTeX_[a-zA-Z0-9_-]+\.woff2)\)', repl_font, katex_css)

            html_out = re.sub(
                r'<link rel="stylesheet" href="[^"]*katex\.min\.css"[^>]*>',
                lambda m: f'<style>\n{katex_css}\n</style>',
                html_out
            )

        if katex_js_file.is_file() and auto_render_js_file.is_file():
            katex_js = katex_js_file.read_text(encoding="utf-8")
            auto_render_js = auto_render_js_file.read_text(encoding="utf-8")
            katex_script_tag = f"<script>\n{katex_js}\n{auto_render_js}\n</script>"
            html_out = re.sub(
                r'<script defer src="[^"]*katex\.min\.js"[^>]*></script>',
                lambda m: katex_script_tag,
                html_out
            )
            html_out = re.sub(
                r'<script defer src="[^"]*auto-render\.min\.js"[^>]*></script>',
                '',
                html_out
            )

    # Replace <script src="app.js"></script> with inline data + app.js
    script_tag = f"""
<script>
window.EMBEDDED_EVOLUTION_DATA = {json.dumps(embedded_payload, ensure_ascii=False)};
</script>
<script>
{app_js}
</script>
"""
    html_out = html_out.replace('<script src="app.js"></script>', script_tag)

    OUTPUT_HTML.write_text(html_out, encoding="utf-8")
    OUTPUT_INDEX.write_text(html_out, encoding="utf-8")
    print(f"Bundled successfully -> {OUTPUT_HTML} and {OUTPUT_INDEX} ({len(html_out):,} bytes)")


if __name__ == "__main__":
    bundle()
