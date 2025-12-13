import asyncio
import os
from pathlib import Path
from typing import List, Optional

from textual import on
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
    Log,
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


class YouTubeMusicSearch(
    ThemeMixin,
    CoverMixin,
    PlaybackMixin,
    SearchMixin,
    App,
):
    """App Textual para buscar y reproducir musica de YouTube Music."""

    CSS = get_theme_css("dark")

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
        self._theme_name: str = "dark"
        self._auto_continue: bool = False
        self._lyrics_task: Optional[asyncio.Task] = None
        self._lyrics_video_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="left"):
                with Container(id="caja-busqueda"):
                    with Horizontal(id="top-menu"):
                        yield Select(options=[], id="audio-select", prompt="Dispositivo audio")
                        yield Button("Salir", id="quit-btn", variant="default")
                        yield Button("Usar cookies", id="use-cookies", variant="default")
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
                            yield Static("Player", id="player-title")
                            with Vertical(id="cover-block"):
                                yield TImage(id="cover")
                                yield LoadingIndicator(id="cover-loading")
                                yield Static("Sin cover", id="cover-status")
                            yield Static("Nada en reproduccion.", id="now-playing")
                            with Vertical(id="progress-block"):
                                yield Static("00:00 / --:--", id="progress-label")
                                yield ProgressBar(total=100, show_percentage=False, id="progress-bar")
                            yield Static("Volumen: --", id="volume-display")
                            yield Checkbox("Continuar", id="auto-continue", value=False)
                            with Horizontal(id="controls"):
                                yield Button("Vol -", id="vol-down", variant="default")
                                yield Button("Vol +", id="vol-up", variant="default")
                            yield Sparkline(id="visualizer")
                    with TabPane("Letras", id="lyrics-tab"):
                        with Container(id="lyrics-content"):
                            yield LoadingIndicator(id="lyrics-loading")
                            yield Static("Sin letra disponible.", id="lyrics-status")
                            yield Log(
                                id="lyrics-text",
                                highlight=False,
                            )
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
            self.visualizer.start()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Visualizador en fallback: {exc}")
        self._load_audio_devices()

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

    def _find_cookies_file(self) -> Optional[Path]:
        return YouTubeMusicClient._discover_cookies()

    def _use_cookies(self) -> None:
        path = self._find_cookies_file()
        if not path:
            self._set_status("No encontre cookies. Coloca cookies.json en ~/.config/ytplayer o en el repo y reintenta.")
            return
        try:
            self.ytmusic = YouTubeMusicClient(str(path))
            self._cookies_path = str(path)
            self._set_status(f"Cookies cargadas: {path}")
            self._reset_lyrics()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"No se pudieron cargar las cookies: {exc}")

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

    def _get_lyrics_log(self) -> Optional[Log]:
        try:
            return self.query_one("#lyrics-text", Log)
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
        log = self._get_lyrics_log()
        if not log:
            return
        try:
            log.clear()
            log.write(message)
        except Exception:
            pass

    def _reset_lyrics(self, message: str = "Sin letra disponible.") -> None:
        if self._lyrics_task:
            self._lyrics_task.cancel()
            self._lyrics_task = None
        self._lyrics_video_id = None
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
                self.ytmusic.get_song_lyrics, item.video_id, item.title, item.artist
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
        log = self._get_lyrics_log()
        if not log:
            return
        try:
            log.clear()
            for line in lyrics.splitlines():
                log.write(line)
        except Exception:
            self._show_lyrics_message("No se pudo mostrar la letra.")

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

    @on(Button.Pressed, "#use-cookies")
    def _on_use_cookies(self, _: Button.Pressed) -> None:
        self._use_cookies()

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
