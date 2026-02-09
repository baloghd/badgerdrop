from pathlib import Path


def load_css_styles() -> str:
    """Load CSS styles from external stylesheet file"""
    css_file = Path(__file__).parent / "styles.css"

    if css_file.exists():
        try:
            return css_file.read_text()
        except Exception:
            return ""
    return ""
