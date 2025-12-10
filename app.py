import asyncio
import math
import random
import io
import requests
from typing import List, Optional
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    ProgressBar,
    Select,
    Sparkline,
    Static,
)
from textual_image.widget import AutoImage as TImage
from modules.models import SearchResult
from modules.player import MPVController
from modules.yt_client import YouTubeMusicClient
from modules.visualizer import Visualizer
from textual.widgets import DataTable
from themes import get_theme_css


class YouTubeMusicSearch(App):
    """Pequena app Textual para buscar en YouTube Music."""

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
    ]

    def __init__(self) -> None:
        super().__init__()
        self.ytmusic = YouTubeMusicClient()
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="left"):
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
                yield DataTable(id="results", zebra_stripes=True, cursor_type="row")
            with Vertical(id="right"):
                yield Static("Player", id="player-title")
                yield Static("Sin cover", id="cover")
                yield Static("Nada en reproduccion.", id="now-playing")
                with Vertical(id="progress-block"):
                    yield Static("00:00 / --:--", id="progress-label")
                    yield ProgressBar(total=100, show_percentage=False, id="progress-bar")
                yield Static("Volumen: --", id="volume-display")
                with Horizontal(id="controls"):
                    yield Button("Vol -", id="vol-down", variant="default")
                    yield Button("Vol +", id="vol-up", variant="default")
                    yield Button("<< 5s", id="seek-back", variant="default")
                    yield Button(">> 5s", id="seek-forward", variant="default")
                yield Sparkline(id="visualizer")
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
        # Intenta arrancar captura de audio real (Pulse monitor). Si falla, cae a fallback.
        try:
            self.visualizer.start()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Visualizador en fallback: {exc}")
        self._load_audio_devices()

    def action_focus_input(self) -> None:
        self.query_one(Input).focus()

    async def action_search(self) -> None:
        query = self.query_one(Input).value.strip()
        if not query:
            self._set_status("Escribe algo para buscar.")
            return

        self._set_status(f"Buscando \"{query}\" en YouTube Music...")
        table = self.query_one(DataTable)
        table.clear()
        self._last_results = []

        if self._current_worker:
            self._current_worker.cancel()

        self._current_worker = asyncio.create_task(self._run_search(query))

    async def _run_search(self, query: str) -> None:
        task = asyncio.current_task()
        try:
            results = await asyncio.to_thread(self._fetch_results, query)
            self._render_results(results, query)
        except asyncio.CancelledError:
            return
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error al buscar: {exc.__class__.__name__} {exc}")
        finally:
            if self._current_worker is task:
                self._current_worker = None

    def _fetch_results(self, query: str) -> List[SearchResult]:
        return self.ytmusic.search_songs(query, limit=20)

    def _render_results(self, results: List[SearchResult], query: str) -> None:
        table = self.query_one(DataTable)
        self._last_results = results
        for row in results:
            table.add_row(row.title, row.artist, row.album, row.duration)
        if results:
            self._set_status(f"{len(results)} resultados para \"{query}\".")
            table.focus()
            try:
                table.move_cursor(row=0, column=0, scroll=False)
            except Exception:
                pass
        else:
            self._set_status(f"Sin resultados para \"{query}\".")

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _load_audio_devices(self) -> None:
        select = self.query_one("#audio-select", Select)
        if not self.player.available:
            select.set_options([("Auto", "auto")])
            return
        try:
            devices = self.player.list_audio_devices()
        except Exception as exc:  # noqa: BLE001
            self._set_status("Audio: auto")
            select.set_options([("Auto", "auto")])
            return
        self._audio_devices = devices
        options = [(desc, name) for name, desc in devices]
        if not options:
            options = [("Auto", "auto")]
        select.set_options(options)
        # marca el primero como seleccionado
        select.value = options[0][1]
        self._selected_device = select.value

    def _update_volume_display(self) -> None:
        self.query_one("#volume-display", Static).update(f"Volumen: {self._volume}%")

    def _set_volume(self, volume: int) -> None:
        self._volume = max(0, min(100, volume))
        if self.player.available:
            try:
                self._volume = self.player.set_volume(self._volume)
            except Exception as exc:  # noqa: BLE001
                self._set_status(f"Error al ajustar volumen: {exc}")
                return
        self._update_volume_display()
        self._set_status(f"Volumen {self._volume}%")

    def action_vol_up(self) -> None:
        self._set_volume(self._volume + 5)

    def action_vol_down(self) -> None:
        self._set_volume(self._volume - 5)

    def action_seek_forward(self) -> None:
        self._seek_relative(self._seek_step)

    def action_seek_back(self) -> None:
        self._seek_relative(-self._seek_step)

    def action_big_seek_forward(self) -> None:
        self._seek_relative(15)

    def action_big_seek_back(self) -> None:
        self._seek_relative(-15)

    def action_cursor_up(self) -> None:
        self._move_cursor(-1)

    def action_cursor_down(self) -> None:
        self._move_cursor(1)

    def _move_cursor(self, delta: int) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        # Ensure focus is on the table
        table.focus()
        current = table.cursor_row if table.cursor_row is not None else 0
        new_index = max(0, min(table.row_count - 1, current + delta))
        try:
            table.move_cursor(row=new_index, scroll=True)
        except Exception:
            return
        # Si estamos pausados y movemos cursor, actualizamos seleccion actual
        if not self._is_playing:
            self._current_index = new_index

    def _seek_relative(self, seconds: int) -> None:
        if not self._current:
            self._set_status("No hay nada reproduciendo.")
            return
        if not self.player.available:
            msg = self.player.last_error or "mpv no esta disponible."
            self._set_status(msg)
            return
        try:
            self.player.seek(seconds)
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error al hacer seek: {exc}")
            return
        direction = "adelante" if seconds > 0 else "atras"
        self._set_status(f"Seek {direction} {abs(seconds)}s")

    def action_play_selected(self) -> None:
        if isinstance(self.focused, Input):
            return
        table = self.query_one(DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            self._set_status("No hay resultados para reproducir.")
            return
        index = table.cursor_row
        if index < 0 or index >= len(self._last_results):
            self._set_status("Seleccion invalida.")
            return
        self._start_playback(self._last_results[index], index)

    def action_play_button(self) -> None:
        self.action_play_selected()

    def action_stop_button(self) -> None:
        self._stop_playback()

    def _start_playback(self, item: SearchResult, index: Optional[int] = None) -> None:
        if not item.url:
            self._set_status("No hay URL para reproducir esta pista.")
            return
        if not self.player.available:
            msg = self.player.last_error or "mpv no esta disponible."
            self._set_status(msg)
            return
        # Si ya hay algo sonando y es otro tema, paramos antes de reproducir.
        if self.player.available and self._current and self._current_index != index:
            try:
                self.player._player.stop()  # type: ignore[attr-defined]
            except Exception:
                pass
        try:
            self.player.set_volume(self._volume)
            self.player.play(item.url)
        except Exception as exc:  # noqa: BLE001
            log = self.player.last_log or ""
            self._set_status(f"Error al reproducir: {exc} {log}")
            return
        self._current = item
        self._current_index = index
        self._is_playing = True
        if self._visualizer_timer:
            self._visualizer_timer.resume()
        self._set_now_playing(item)
        self._set_status(f"Reproduciendo \"{item.title}\" - {item.artist}")
        self._update_play_button()
        self._load_cover(item)

    def action_toggle_play(self) -> None:
        if isinstance(self.focused, Input):
            return
        table = self.query_one(DataTable)
        selected_index = table.cursor_row if table.cursor_row is not None else None
        if not self._current:
            # Si no hay nada reproduciendo, intenta iniciar con la fila seleccionada.
            if selected_index is not None and 0 <= selected_index < len(self._last_results):
                self._start_playback(self._last_results[selected_index], selected_index)
            else:
                self._set_status("No hay seleccion para reproducir.")
            return
        if not self.player.available:
            msg = self.player.last_error or "mpv no esta disponible."
            self._set_status(msg)
            return
        # Si hay otra fila seleccionada, cambia de tema en lugar de pausar.
        if (
            selected_index is not None
            and 0 <= selected_index < len(self._last_results)
            and selected_index != self._current_index
        ):
            self._start_playback(self._last_results[selected_index], selected_index)
            return
        # Aqui entra el toggle play/pause.
        try:
            is_playing = self.player.toggle_pause()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Error al pausar/reanudar: {exc}")
            return
        self._is_playing = is_playing
        if self._is_playing:
            if self._visualizer_timer:
                self._visualizer_timer.resume()
            self._set_status(f"Reproduciendo \"{self._current.title}\".")
        else:
            if self._visualizer_timer:
                self._visualizer_timer.pause()
            self._set_status("Pausa.")
        self._update_play_button()

    def _set_now_playing(self, item: SearchResult) -> None:
        text = f"Titulo: {item.title}\nArtista: {item.artist}\nAlbum: {item.album}\nDuracion: {item.duration}"
        self.query_one("#now-playing", Static).update(text)
        self._reset_progress()

    def _stop_playback(self) -> None:
        if not self._current:
            return
        try:
            if self.player.available:
                self.player._player.stop()  # type: ignore[attr-defined]
        except Exception:
            pass
        self._is_playing = False
        self._current = None
        self._current_index = None
        if self._visualizer_timer:
            self._visualizer_timer.pause()
        self._set_status("Stop.")
        self._set_now_playing(SearchResult("Sin titulo", "-", "-", "-", "", ""))
        self._update_play_button()
        self._reset_progress()
        self._reset_visualizer()
        self._reset_cover()

    def _tick_visualizer(self) -> None:
        spark = self.query_one("#visualizer", Sparkline)
        if not self._is_playing or not self._current:
            self._reset_visualizer()
            return
        # Energia real desde visualizer si disponible; si no, fallback.
        energy = self.visualizer.get_energy() if self.visualizer else 0.0
        if energy <= 0.0:
            if self.player.available:
                try:
                    energy = self.player.sample_energy()
                except Exception:
                    energy = 0.0
            else:
                energy = 0.0
        value = max(0.0, min(1.0, energy))
        self._spark_data.append(value)
        self._spark_data = self._spark_data[-80:]
        spark.data = list(self._spark_data)

    def _reset_visualizer(self) -> None:
        try:
            spark = self.query_one("#visualizer", Sparkline)
            self._spark_data = []
            spark.data = []
        except Exception:
            pass

    def _tick_progress(self) -> None:
        bar = self.query_one("#progress-bar", ProgressBar)
        label = self.query_one("#progress-label", Static)
        if not self._is_playing or not self._current or not self.player.available:
            bar.progress = 0
            label.update("00:00 / --:--")
            return
        pos, dur = self.player.get_time_info()
        if pos is None or dur is None or dur <= 0:
            bar.progress = 0
            label.update("00:00 / --:--")
            return
        percent = max(0.0, min(1.0, pos / dur))
        bar.progress = int(percent * 100)
        label.update(f"{self._fmt_time(pos)} / {self._fmt_time(dur)}")

    def _reset_progress(self) -> None:
        try:
            self.query_one("#progress-bar", ProgressBar).progress = 0
            self.query_one("#progress-label", Static).update("00:00 / --:--")
        except Exception:
            pass

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        try:
            secs = int(seconds)
            m, s = divmod(secs, 60)
            h, m = divmod(m, 60)
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"
        except Exception:
            return "00:00"

    def _load_cover(self, item: SearchResult) -> None:
        if self._cover_task:
            self._cover_task.cancel()
        if not item.thumbnail_url:
            self._reset_cover()
            return
        self._set_status("Cargando cover...")
        self._cover_task = asyncio.create_task(self._load_cover_async(item.thumbnail_url))

    async def _load_cover_async(self, url: str) -> None:
        try:
            data = await asyncio.to_thread(self._fetch_image_bytes, url)
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Cover error: {exc}")
            return
        try:
            self.call_from_thread(self._update_cover_widget, data)
            self.call_from_thread(self._set_status, "Cover cargada")
        except Exception:
            pass

    @staticmethod
    def _fetch_image_bytes(url: str) -> bytes:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content

    def _update_cover_widget(self, data: bytes) -> None:
        cover = self.query_one("#cover", TImage)
        cover.image = data
        try:
            status = self.query_one("#cover-status", Static)
            status.update("")
        except Exception:
            pass

    def _reset_cover(self) -> None:
        try:
            cover = self.query_one("#cover", TImage)
            cover.image = None
        except Exception:
            pass
        try:
            status = self.query_one("#cover-status", Static)
            status.update("Sin cover")
        except Exception:
            pass

    def on_unmount(self) -> None:
        try:
            self.visualizer.stop()
        except Exception:
            pass
        self._update_play_button()

    def _update_play_button(self) -> None:
        try:
            btn = self.query_one("#btn-play", Button)
            btn.label = "Pause" if self._is_playing else "Play"
        except Exception:
            return

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
        # Ejecuta play al seleccionar fila (click/doble click)
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
        self.action_play_button()

    @on(Button.Pressed, "#btn-stop")
    def _on_btn_stop(self, _: Button.Pressed) -> None:
        self.action_stop_button()

    @on(Button.Pressed, "#btn-next")
    def _on_btn_next(self, _: Button.Pressed) -> None:
        self.action_big_seek_forward()

    @on(Button.Pressed, "#btn-prev")
    def _on_btn_prev(self, _: Button.Pressed) -> None:
        self.action_big_seek_back()


if __name__ == "__main__":
    app = YouTubeMusicSearch()
    app.run()
