"""Theme loader for the app."""

from . import dark, dracula, caramel, light, mini  # noqa: F401

THEMES = {
    "dark": "dark",
    "dracula": "dracula",
    "caramel": "caramel",
    "light": "light",
    "mini": "mini",
}


def get_theme_css(name: str) -> str:
    """Return CSS string for a given theme name."""
    name = (name or "").lower()
    if name == "dracula":
        from .dracula import THEME_CSS

        return THEME_CSS
    if name == "caramel":
        from .caramel import THEME_CSS

        return THEME_CSS
    if name == "light":
        from .light import THEME_CSS

        return THEME_CSS
    if name == "mini":
        from .mini import THEME_CSS

        return THEME_CSS
    from .dark import THEME_CSS

    return THEME_CSS
