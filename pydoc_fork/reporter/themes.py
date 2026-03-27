"""
Themes definitions
"""

from typing import Dict

THEMES: Dict[str, Dict[str, str]] = {
    "classic": {
        "bg-color": "#f0f0f8",
        "text-color": "#000000",
        "link-color": "#0000ee",
        "heading-bg": "#7799ee",
        "heading-text": "#ffffff",
        "section-bg": "#ee77aa",
        "section-text": "#ffffff",
        "sub-section-bg": "#aa55cc",
        "sub-section-text": "#ffffff",
        "data-bg": "#55aa55",
        "data-text": "#ffffff",
        "disabled-text": "#909090",
        "repr-color": "#c040c0",
    },
    "light": {
        "bg-color": "#ffffff",
        "text-color": "#2c3e50",
        "link-color": "#3498db",
        "heading-bg": "#34495e",
        "heading-text": "#ffffff",
        "section-bg": "#ecf0f1",
        "section-text": "#2c3e50",
        "sub-section-bg": "#dee2e6",
        "sub-section-text": "#2c3e50",
        "data-bg": "#d4edda",
        "data-text": "#155724",
        "disabled-text": "#6c757d",
        "repr-color": "#e83e8c",
    },
    "dark": {
        "bg-color": "#1e1e1e",
        "text-color": "#d4d4d4",
        "link-color": "#3794ff",
        "heading-bg": "#333333",
        "heading-text": "#cccccc",
        "section-bg": "#252526",
        "section-text": "#cccccc",
        "sub-section-bg": "#2d2d2d",
        "sub-section-text": "#cccccc",
        "data-bg": "#1e3a1e",
        "data-text": "#b5cea8",
        "disabled-text": "#808080",
        "repr-color": "#ce9178",
    },
}


def get_theme_css(theme_name: str) -> str:
    """Generate CSS variables for a theme"""
    theme = THEMES.get(theme_name, THEMES["classic"])
    css_vars = "\n".join([f"    --{key}: {value};" for key, value in theme.items()])
    return f":root {{\n{css_vars}\n}}"
