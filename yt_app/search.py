import asyncio
from typing import List

from textual.widgets import DataTable, Input

from modules.models import SearchResult


class SearchMixin:
    """Busqueda de canciones y navegacion por la tabla."""

    _current_worker: asyncio.Task | None
    _last_results: List[SearchResult]

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

    def action_cursor_up(self) -> None:
        self._move_cursor(-1)

    def action_cursor_down(self) -> None:
        self._move_cursor(1)

    def _move_cursor(self, delta: int) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        table.focus()
        current = table.cursor_row if table.cursor_row is not None else 0
        new_index = max(0, min(table.row_count - 1, current + delta))
        try:
            table.move_cursor(row=new_index, scroll=True)
        except Exception:
            return
        if not self._is_playing:
            self._current_index = new_index
