from typing import List, Optional

from textual.widgets import Button, DataTable, Input, ProgressBar, Sparkline, Static

from modules.models import SearchResult


class PlaybackMixin:
    """Control de reproduccion, volumen y progreso."""

    _current: Optional[SearchResult]
    _current_index: Optional[int]
    _spark_data: List[float]
    _volume: int
    _seek_step: int
    _is_playing: bool
    _auto_continue: bool

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
        try:
            self.player.set_normalizer(getattr(self, "_normalize_volume", False))
        except Exception:
            pass
        try:
            self._load_lyrics(item)
        except Exception:
            pass

    def action_toggle_play(self) -> None:
        if isinstance(self.focused, Input):
            return
        table = self.query_one(DataTable)
        selected_index = table.cursor_row if table.cursor_row is not None else None
        if not self._current:
            if selected_index is not None and 0 <= selected_index < len(self._last_results):
                self._start_playback(self._last_results[selected_index], selected_index)
            else:
                self._set_status("No hay seleccion para reproducir.")
            return
        if not self.player.available:
            msg = self.player.last_error or "mpv no esta disponible."
            self._set_status(msg)
            return
        if (
            selected_index is not None
            and 0 <= selected_index < len(self._last_results)
            and selected_index != self._current_index
        ):
            self._start_playback(self._last_results[selected_index], selected_index)
            return
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
        try:
            self._reset_lyrics()
        except Exception:
            pass

    def _tick_visualizer(self) -> None:
        spark = self.query_one("#visualizer", Sparkline)
        if not self._is_playing or not self._current:
            self._reset_visualizer()
            return
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

    def _handle_track_end(self) -> None:
        """Callback cuando mpv informa fin de archivo."""
        self._is_playing = False
        if self._auto_continue and self._current_index is not None:
            next_index = self._current_index + 1
            if 0 <= next_index < len(self._last_results):
                self._start_playback(self._last_results[next_index], next_index)
                return
        self._stop_playback()

    def _tick_progress(self) -> None:
        bar = self.query_one("#progress-bar", ProgressBar)
        label = self.query_one("#progress-label", Static)
        if not self._is_playing or not self._current or not self.player.available:
            bar.progress = 0
            label.update("00:00 / --:--")
            return
        pos, dur, percent = self.player.get_time_info()
        # Derivar porcentaje si faltara pero hay pos/dur.
        if percent is None and pos is not None and dur and dur > 0:
            percent = (pos / dur) * 100.0
        # Validar porcentaje.
        if percent is not None:
            percent = max(0.0, min(100.0, percent))
            bar.progress = int(percent)
        else:
            bar.progress = 0

        if pos is not None and dur is not None and dur > 0:
            label.update(f"{self._fmt_time(pos)} / {self._fmt_time(dur)}")
        else:
            label.update("00:00 / --:--")

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

    def _update_play_button(self) -> None:
        try:
            btn = self.query_one("#btn-play", Button)
            btn.label = "Pause" if self._is_playing else "Play"
        except Exception:
            return
