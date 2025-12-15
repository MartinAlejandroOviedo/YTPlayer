import asyncio
import os
import re
from pathlib import Path
from typing import List, Optional, Any

from textual import on
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    LoadingIndicator,
    ProgressBar,
    Select,
    Sparkline,
    Static,
    TabPane,
    TabbedContent,
)
from textual_image.widget import AutoImage as TImage

from modules.models import SearchResult
from modules.player import MPVController
from modules.visualizer import Visualizer
from modules.yt_client import YouTubeMusicClient
from themes import get_theme_css
from yt_app.cover import CoverMixin
from yt_app.playback import PlaybackMixin
from yt_app.search import SearchMixin
from yt_app.theme import ThemeMixin


class LyricsTable(DataTable):
    """Tabla de solo lectura para letras."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[override]
        super().__init__(*args, **kwargs)
        self.show_cursor = False
        self.cursor_type = "none"
        try:
            self.can_focus = False  # type: ignore[attr-defined]
        except Exception:
            pass

    def on_focus(self, event: events.Focus) -> None:  # pragma: no cover
        event.prevent_default()

    def on_key(self, event: events.Key) -> None:  # pragma: no cover
        event.prevent_default()

    def on_mouse_down(self, event: events.MouseDown) -> None:  # pragma: no cover
        event.prevent_default()


class YouTubeMusicSearch(
    ThemeMixin,
    CoverMixin,
    PlaybackMixin,
    SearchMixin,
    App,
):
    """App Textual para buscar y reproducir musica de YouTube Music."""

    CSS = get_theme_css("mini")

    BINDINGS = [
        ("ctrl+c", "quit", "Salir"),
        ("/", "focus_input", "Buscar"),
        ("enter", "play_selected", "Play"),
        ("space", "toggle_play", "Play/Pause"),
        ("-", "vol_down", "Vol -"),
        ("=", "vol_up", "Vol +"),
        ("left", "seek_back", "-5s"),
        ("right", "seek_forward", "+5s"),
        ("up", "cursor_up", "Arriba"),
        ("down", "cursor_down", "Abajo"),
        ("ctrl+1", "set_theme('dark')", "Tema dark"),
        ("ctrl+2", "set_theme('dracula')", "Tema dracula"),
        ("ctrl+3", "set_theme('caramel')", "Tema caramel"),
        ("ctrl+4", "set_theme('light')", "Tema light"),
        ("ctrl+5", "set_theme('mini')", "Tema mini"),
    ]

    def __init__(self) -> None:
        super().__init__()
        # Intenta usar cookies automaticamente si existen.
        detected = self._find_cookies_file()
        self._cookies_path: Optional[str] = str(detected) if detected else None
        self.ytmusic = YouTubeMusicClient(self._cookies_path)
        self.player = MPVController()
        self.visualizer = Visualizer(mpv_player=self.player._player)
        self._current_worker: Optional[asyncio.Task] = None
        self._last_results: List[SearchResult] = []
        self._current: Optional[SearchResult] = None
        self._current_index: Optional[int] = None
        self._is_playing: bool = False
        self._visualizer_timer = None
        self._progress_timer = None
        self._volume: int = 50
        self._seek_step: int = 5
        self._visual_phase: float = 0.0
        self._audio_devices: list[tuple[str, str]] = []
        self._selected_device: Optional[str] = None
        self._spark_data: List[float] = []
        self._cover_task: Optional[asyncio.Task] = None
        self._theme_name: str = "mini"
        self._auto_continue: bool = False
        self._lyrics_task: Optional[asyncio.Task] = None
        self._lyrics_video_id: Optional[str] = None
        self._normalize_volume: bool = True
        self._eq_preset: str = "plano"
        self._lyrics_lines: List[str] = []
        self._synced_lyrics: List[dict[str, Any]] = []
        self._current_lyric_index: int = -1

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="left"):
                with Container(id="caja-busqueda"):
                    with Horizontal(id="top-menu"):
                        yield Select(options=[], id="audio-select", prompt="Dispositivo audio")
                        yield Button("Salir", id="quit-btn", variant="default")
                    with Container(id="search-area"):
                        yield Static("Busca en YouTube Music", id="title")
                        with Horizontal():
                            yield Input(
                                placeholder="Escribe tu consulta y Enter", id="query"
                            )
                            yield Button("Buscar", id="search-btn", variant="primary")
                        yield Static("", id="status")
                    with Horizontal(id="transport"):
                        yield Button("<<", id="btn-prev", variant="default")
                        yield Button("Play", id="btn-play", variant="primary")
                        yield Button("Stop", id="btn-stop", variant="warning")
                        yield Button(">>", id="btn-next", variant="default")
                with Container(id="caja-listado"):
                    yield DataTable(id="results", zebra_stripes=True, cursor_type="row")
            with Vertical(id="right"):
                with TabbedContent(id="right-tabs"):
                    with TabPane("Player", id="player-tab"):
                        with Container(id="caja-player"):
                            with Vertical(id="cover-block"):
                                yield TImage(id="cover")
                                yield LoadingIndicator(id="cover-loading")
                                yield Static("Sin cover", id="cover-status")
                            yield Static("Nada en reproduccion.", id="now-playing")
                            with Vertical(id="progress-block"):
                                yield Static("00:00 / --:--", id="progress-label")
                                yield ProgressBar(total=100, show_percentage=False, id="progress-bar")
                            yield Static("Volumen: --", id="volume-display")
                            with Horizontal(id="controls"):
                                yield Button("Vol -", id="vol-down", variant="default")
                                yield Button("Vol +", id="vol-up", variant="default")
                            yield Sparkline(id="visualizer")
                    with TabPane("Opciones", id="options-tab"):
                        with Container(id="options-content"):
                            yield Static("Ajustes de reproduccion", id="options-title")
                            yield Select(
                                options=[
                                    ("Plano", "plano"),
                                    ("Rock", "rock"),
                                    ("Pop", "pop"),
                                    ("Jazz", "jazz"),
                                    ("House", "house"),
                                    ("Techno", "techno"),
                                ],
                                id="eq-select",
                                prompt="Ecualizador",
                                value="plano",
                            )
                            yield Checkbox("Continuar", id="auto-continue", value=False)
                            yield Checkbox("Normalizar", id="normalize", value=True)
                    with TabPane("Letras", id="lyrics-tab"):
                        with Container(id="lyrics-content"):
                            yield LoadingIndicator(id="lyrics-loading")
                            yield Static("Sin letra disponible.", id="lyrics-status")
                            yield LyricsTable(id="lyrics-table", zebra_stripes=True, cursor_type="none")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Titulo", "Artista", "Album", "Duracion")
        self.query_one(Input).focus()
        self._visualizer_timer = self.set_interval(0.2, self._tick_visualizer, pause=True)
        self._progress_timer = self.set_interval(0.5, self._tick_progress, pause=False)
        if not self.player.available and self.player.last_error:
            self._set_status(self.player.last_error)
        self._update_volume_display()
        self._reset_lyrics()
        try:
            self.player.set_end_callback(lambda: self.call_from_thread(self._handle_track_end))
        except Exception:
            pass
        try:
            self.query_one("#auto-continue", Checkbox).value = self._auto_continue
        except Exception:
            pass
        try:
            self.query_one("#normalize", Checkbox).value = self._normalize_volume
        except Exception:
            pass
        try:
            eq_select = self.query_one("#eq-select", Select)
            eq_select.value = self._eq_preset
        except Exception:
            pass
        self._apply_filters()
        try:
            self.visualizer.start()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Visualizador en fallback: {exc}")
        self._load_audio_devices()
        self._init_lyrics_table()

    def _load_audio_devices(self) -> None:
        select = self.query_one("#audio-select", Select)
        if not self.player.available:
            select.set_options([("Auto", "auto")])
            return
        try:
            devices = self.player.list_audio_devices()
        except Exception:  # noqa: BLE001
            self._set_status("Audio: auto")
            select.set_options([("Auto", "auto")])
            return
        self._audio_devices = devices
        options = [(desc, name) for name, desc in devices]
        if not options:
            options = [("Auto", "auto")]
        select.set_options(options)
        select.value = options[0][1]
        self._selected_device = select.value

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _apply_filters(self) -> None:
        """Aplica normalizador + preset de EQ activos."""
        if not self.player.available:
            return
        try:
            self.player.set_filters(self._normalize_volume, self._eq_preset)
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error al ajustar filtros: {exc}")

    def _find_cookies_file(self) -> Optional[Path]:
        return YouTubeMusicClient._discover_cookies()

    def _init_lyrics_table(self) -> None:
        table = self._get_lyrics_table()
        if not table:
            return
        if table.columns:
            return
        try:
            table.add_columns("Tiempo", "Texto")
            try:
                table.can_focus = False  # type: ignore[attr-defined]
            except Exception:
                pass
            for attr, value in (("show_cursor", False), ("cursor_type", "none")):
                try:
                    setattr(table, attr, value)
                except Exception:
                    continue
        except Exception:
            pass

    def _get_lyrics_status_widget(self) -> Optional[Static]:
        try:
            return self.query_one("#lyrics-status", Static)
        except Exception:
            return None

    def _get_lyrics_loader(self) -> Optional[LoadingIndicator]:
        try:
            return self.query_one("#lyrics-loading", LoadingIndicator)
        except Exception:
            return None

    def _get_lyrics_table(self) -> Optional[DataTable]:
        try:
            return self.query_one("#lyrics-table", DataTable)
        except Exception:
            return None

    def _set_lyrics_loading(self, visible: bool) -> None:
        loader = self._get_lyrics_loader()
        if not loader:
            return
        try:
            loader.display = visible  # type: ignore[attr-defined]
        except Exception:
            try:
                loader.styles.display = "block" if visible else "none"
            except Exception:
                pass

    def _set_lyrics_status(self, message: str) -> None:
        status_widget = self._get_lyrics_status_widget()
        if status_widget:
            status_widget.update(message)

    def _show_lyrics_message(self, message: str) -> None:
        table = self._get_lyrics_table()
        if not table:
            self.call_after_refresh(lambda: self._show_lyrics_message(message))
            return
        try:
            table.clear()
            if not table.columns:
                table.add_columns("Tiempo", "Texto")
            table.add_row("", message)
        except Exception:
            pass

    def _reset_lyrics(self, message: str = "Sin letra disponible.") -> None:
        if self._lyrics_task:
            self._lyrics_task.cancel()
            self._lyrics_task = None
        self._lyrics_video_id = None
        self._lyrics_lines = []
        self._synced_lyrics = []
        self._current_lyric_index = -1
        self._set_lyrics_loading(False)
        self._set_lyrics_status(message)
        self._show_lyrics_message(message)

    def _load_lyrics(self, item: SearchResult) -> None:
        if self._lyrics_task:
            self._lyrics_task.cancel()
            self._lyrics_task = None
        self._lyrics_video_id = item.video_id
        self._set_lyrics_loading(True)
        self._set_lyrics_status("Buscando letra...")
        self._show_lyrics_message("Buscando letra...")
        if not item.video_id:
            self._set_lyrics_loading(False)
            self._set_lyrics_status("Letra no disponible para esta pista.")
            self._show_lyrics_message("Letra no disponible para esta pista.")
            return
        self._lyrics_task = asyncio.create_task(self._load_lyrics_async(item))

    async def _load_lyrics_async(self, item: SearchResult) -> None:
        task = asyncio.current_task()
        try:
            lyrics = await asyncio.to_thread(
                self.ytmusic.get_song_lyrics,
                item.video_id,
                item.title,
                item.artist,
                item.album,
                item.duration,
            )
            if self._lyrics_video_id != item.video_id:
                return
            if lyrics:
                self._set_lyrics_text(lyrics)
                source = getattr(self.ytmusic, "last_lyrics_source", "") or ""
                status_msg = f"Letra cargada ({source})." if source else "Letra cargada."
                self._set_lyrics_status(status_msg)
            else:
                self._set_lyrics_status("Letra no disponible.")
                self._show_lyrics_message("Letra no disponible.")
        except asyncio.CancelledError:
            return
        except Exception as exc:  # noqa: BLE001
            if self._lyrics_video_id == item.video_id:
                self._set_lyrics_status(f"Error al obtener letra: {exc}")
                self._show_lyrics_message("Error al obtener letra.")
        finally:
            if self._lyrics_task is task:
                self._lyrics_task = None
            self._set_lyrics_loading(False)

    def _set_lyrics_text(self, lyrics: str) -> None:
        try:
            plain_lines, synced = self._parse_lyrics(lyrics)
            self._lyrics_lines = plain_lines
            self._synced_lyrics = synced
            self._current_lyric_index = -1
            self._set_status(f"Letras cargadas ({len(self._lyrics_lines)} lineas)")
            self._render_lyrics_lines()
        except Exception:
            self._show_lyrics_message("No se pudo mostrar la letra.")

    def _render_lyrics_lines(self, active_index: Optional[int] = None) -> None:
        table = self._get_lyrics_table()
        if not table:
            self.call_after_refresh(lambda: self._render_lyrics_lines(active_index))
            return
        try:
            if not table.columns:
                table.add_columns("Tiempo", "Texto")
            table.clear()
            if not self._lyrics_lines:
                table.add_row("", "Sin letra disponible.")
                return
            for idx, line in enumerate(self._lyrics_lines):
                prefix = "▶ " if active_index is not None and idx == active_index else "  "
                time_str = ""
                if idx < len(self._synced_lyrics):
                    time_str = self._synced_lyrics[idx].get("time", "")
                text = f"{prefix}{line}"
                table.add_row(time_str, text, key=f"lyric-{idx}")
            if active_index is not None and 0 <= active_index < len(self._lyrics_lines):
                try:
                    table.scroll_to_row(active_index)
                except Exception:
                    pass
        except Exception:
            self._show_lyrics_message("No se pudo mostrar la letra.")

    @staticmethod
    def _parse_lyrics(lyrics: str) -> tuple[list[str], list[dict[str, Any]]]:
        """Devuelve (lineas sin timestamp, lista sincronizada con ts y texto)."""
        timestamp_re = re.compile(r"\[([0-9]{1,2}):([0-9]{2})(?:\.([0-9]{1,3}))?\]")
        synced: list[dict[str, Any]] = []
        plain_lines: list[str] = []

        for raw_line in lyrics.splitlines():
            matches = list(timestamp_re.finditer(raw_line))
            text_start = matches[-1].end() if matches else 0
            text = raw_line[text_start:].strip()
            if matches:
                for match in matches:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    millis = int((match.group(3) or "0").ljust(3, "0"))
                    ts = minutes * 60 + seconds + millis / 1000.0
                    synced.append({"ts": ts, "text": text})
            if text:
                plain_lines.append(text)

        if synced:
            synced.sort(key=lambda t: t["ts"])
            # Enriquecer con tiempo formateado.
            for item in synced:
                item["time"] = YouTubeMusicSearch._fmt_ts(item["ts"])
            if not plain_lines:
                plain_lines = [item["text"] for item in synced]
        else:
            # Algunos providers devuelven todo en una sola linea con dobles espacios o con '\n' literal.
            normalized = lyrics.replace("\\n", "\n")
            normalized = re.sub(r"[ \t]{2,}", "\n", normalized)
            plain_lines = [line.strip() for line in normalized.splitlines() if line.strip()]

        return (plain_lines, synced)

    def _update_synced_highlight(self, position: float) -> None:
        if not self._synced_lyrics or position is None:
            return
        idx = self._find_lyric_index(position)
        if idx != self._current_lyric_index:
            self._current_lyric_index = idx
            self._render_lyrics_lines(active_index=idx)

    def _find_lyric_index(self, position: float) -> int:
        idx = -1
        for i, item in enumerate(self._synced_lyrics):
            ts = item.get("ts", 0.0)
            if position >= ts:
                idx = i
            else:
                break
        return idx

    @staticmethod
    def _fmt_ts(seconds: float) -> str:
        try:
            secs = int(seconds)
            m, s = divmod(secs, 60)
            return f"{m:02d}:{s:02d}"
        except Exception:
            return ""

    @on(events.MouseDown, "#lyrics-table")
    def _block_lyrics_click(self, event: events.MouseDown) -> None:
        """Evita que clicks en la tabla de letras rompan el foco/estado."""
        event.stop()

    def on_unmount(self) -> None:
        try:
            self.visualizer.stop()
        except Exception:
            pass
        self._update_play_button()

    @on(Select.Changed, "#audio-select")
    def _on_audio_changed(self, event: Select.Changed) -> None:
        if not self.player.available:
            return
        new_device = event.value
        if not new_device or new_device == self._selected_device:
            return
        if not isinstance(new_device, str):
            return
        try:
            self.player.set_audio_device(new_device)
            self._selected_device = new_device
            self._set_status(f"Audio: {new_device}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error audio device: {exc}")

    @on(Button.Pressed, "#quit-btn")
    def _on_quit(self, _: Button.Pressed) -> None:
        self.exit()

    @on(Input.Submitted)
    async def _on_input_submitted(self, _: Input.Submitted) -> None:
        await self.action_search()

    @on(Button.Pressed, "#search-btn")
    async def _on_search_button(self, _: Button.Pressed) -> None:
        await self.action_search()

    @on(DataTable.RowSelected)
    def _on_row_selected(self, event: DataTable.RowSelected) -> None:
        self.action_play_selected()
        self._current_index = event.cursor_row

    @on(Button.Pressed, "#vol-up")
    def _on_vol_up(self, _: Button.Pressed) -> None:
        self.action_vol_up()

    @on(Button.Pressed, "#vol-down")
    def _on_vol_down(self, _: Button.Pressed) -> None:
        self.action_vol_down()

    @on(Checkbox.Changed, "#normalize")
    def _on_normalize_changed(self, event: Checkbox.Changed) -> None:
        self._normalize_volume = bool(event.value)
        self._apply_filters()
        msg = "Normalizacion activada" if self._normalize_volume else "Normalizacion desactivada"
        self._set_status(msg)

    @on(Select.Changed, "#eq-select")
    def _on_eq_changed(self, event: Select.Changed) -> None:
        value = event.value
        if not isinstance(value, str):
            return
        self._eq_preset = value
        self._apply_filters()
        self._set_status(f"Ecualizador: {value}")

    @on(Button.Pressed, "#seek-forward")
    def _on_seek_forward_btn(self, _: Button.Pressed) -> None:
        self.action_seek_forward()

    @on(Button.Pressed, "#seek-back")
    def _on_seek_back_btn(self, _: Button.Pressed) -> None:
        self.action_seek_back()

    @on(Button.Pressed, "#btn-play")
    def _on_btn_play(self, _: Button.Pressed) -> None:
        self.action_toggle_play()

    @on(Button.Pressed, "#btn-stop")
    def _on_btn_stop(self, _: Button.Pressed) -> None:
        self.action_stop_button()

    @on(Button.Pressed, "#btn-next")
    def _on_btn_next(self, _: Button.Pressed) -> None:
        self.action_big_seek_forward()

    @on(Button.Pressed, "#btn-prev")
    def _on_btn_prev(self, _: Button.Pressed) -> None:
        self.action_big_seek_back()

    @on(Checkbox.Changed, "#auto-continue")
    def _on_auto_continue_changed(self, event: Checkbox.Changed) -> None:
        self._auto_continue = bool(event.value)
        msg = "Continuar auto: on" if self._auto_continue else "Continuar auto: off"
        self._set_status(msg)


__all__ = ["YouTubeMusicSearch"]
