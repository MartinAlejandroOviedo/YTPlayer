from typing import Optional

try:
    import mpv  # type: ignore
except Exception:
    mpv = None


class MPVController:
    """Wrapper sencillo sobre python-mpv."""

    def __init__(self) -> None:
        self._player = None
        self._error: Optional[str] = None
        self._last_log: Optional[str] = None
        if mpv is None:
            self._error = "libmpv no esta disponible. Instala mpv/libmpv."
            return
        try:
            # video=False evita abrir ventana; ytdl=True permite URLs de YouTube.
            self._player = mpv.MPV(
                ytdl=True,
                video=False,
                vo="null",
                log_handler=self._on_log,
            )
            self._register_events()
        except Exception as exc:  # noqa: BLE001
            self._error = str(exc)

    @property
    def available(self) -> bool:
        return self._player is not None

    @property
    def last_error(self) -> Optional[str]:
        return self._error

    @property
    def last_log(self) -> Optional[str]:
        return self._last_log

    def play(self, url: str) -> None:
        if not self._player:
            raise RuntimeError(self._error or "mpv no inicializado")
        self._last_log = None
        self._player.play(url)
        self._player.pause = False

    def toggle_pause(self) -> bool:
        if not self._player:
            raise RuntimeError(self._error or "mpv no inicializado")
        new_state = not bool(getattr(self._player, "pause", False))
        self._player.pause = new_state
        return not new_state  # True si queda reproduciendo

    def set_volume(self, volume: int) -> int:
        """Ajusta volumen (0-100) y devuelve el valor fijado."""
        vol = max(0, min(100, int(volume)))
        if not self._player:
            raise RuntimeError(self._error or "mpv no inicializado")
        self._player.volume = vol
        return vol

    def seek(self, seconds: float) -> None:
        """Seek relativo en segundos."""
        if not self._player:
            raise RuntimeError(self._error or "mpv no inicializado")
        # reference=relative mueve desde la posicion actual.
        self._player.command("seek", seconds, "relative")

    def sample_energy(self) -> float:
        """Devuelve un estimado 0-1 de energia basada en bitrate y volumen."""
        if not self._player:
            raise RuntimeError(self._error or "mpv no inicializado")
        bitrate = 0.0
        try:
            # audio-bitrate suele venir en bits/s
            bitrate = float(self._player.command("get_property", "audio-bitrate") or 0.0)
        except Exception:
            bitrate = 0.0
        try:
            volume = float(self._player.volume or 0.0) / 100.0
        except Exception:
            volume = 0.5
        # Normalizamos bitrate a 320 kbps aprox.
        normalized_br = min(1.0, bitrate / 320_000.0) if bitrate > 0 else 0.2
        level = max(0.0, min(1.0, normalized_br * (0.5 + volume / 2)))
        return level

    def _on_log(self, level: str, prefix: str, text: str) -> None:
        if level.lower() in {"error", "warning"}:
            self._last_log = f"{prefix}: {text}"

    def _register_events(self) -> None:
        if not self._player:
            return

        @self._player.event_callback("end-file")
        def _end_file(event):  # type: ignore
            # reason 'error' or error code set.
            reason = getattr(event, "reason", None)
            error = getattr(event, "error", None)
            if reason == "error" or error not in (0, None):
                self._last_log = f"end-file error: reason={reason}, code={error}"
