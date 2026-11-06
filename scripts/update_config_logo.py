from pathlib import Path

p = Path("utils/config.py")
text = p.read_text(encoding="utf-8")
text_norm = text.replace("\r\n", "\n")

start = text_norm.find("# ── Logo Configuration ──")
end = text_norm.find("def _resolve_logo_path() -> Path:")

if start != -1 and end != -1:
    replacement = (
        "# ── Logo Configuration ──\n"
        "# Sacred Euclidean Rub el Hizb + Calligraphic 'Haa' (هـ) + Open Mushaf vector emblem\n"
        '_DEFAULT_LOGO_PATH = _APP_DIR / "hidayah_logo.svg"\n'
        '_DEFAULT_LOGO_SVG = _DEFAULT_LOGO_PATH.read_text(encoding="utf-8") if _DEFAULT_LOGO_PATH.exists() else ""\n\n\n'
    )
    new_text = text_norm[:start] + replacement + text_norm[end:]
    p.write_text(new_text, encoding="utf-8")
    print("Updated utils/config.py successfully.")
else:
    print(f"Error: Markers not found. start={start}, end={end}")
