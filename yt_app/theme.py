from themes import get_theme_css


class ThemeMixin:
    """Cambio dinamico de tema."""

    _theme_name: str
    _theme_source_key: tuple[str, str] | None = None

    def action_set_theme(self, name: str) -> None:
        css = get_theme_css(name)
        if self._theme_source_key:
            self.stylesheet.source.pop(self._theme_source_key, None)
        key = ("theme", name)
        self.stylesheet.add_source(css, read_from=key)
        self._theme_source_key = key
        self.refresh_css()
        self._theme_name = name
        self._set_status(f"Tema: {name}")
