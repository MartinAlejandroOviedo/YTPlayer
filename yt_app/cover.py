import asyncio
import io
from typing import Optional

import requests
from PIL import Image as PILImage
from textual.widgets import Static
from textual_image.widget import AutoImage as TImage

from modules.models import SearchResult


class CoverMixin:
    """Carga y fallback de caratulas."""

    _cover_task: asyncio.Task | None

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
        except Exception as exc:
            self.call_from_thread(self._set_status, f"Cover error: {exc}")

    @staticmethod
    def _fetch_image_bytes(url: str) -> bytes:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content

    def _pixelate_to_text(self, data: bytes, max_size: tuple[int, int] = (32, 20)) -> str:
        """Convierte la imagen a un pequeño ascii-art para fallback."""
        with PILImage.open(io.BytesIO(data)) as img:
            img = img.convert("RGB")
            img.thumbnail(max_size)
            palette = " .:-=+*#%@"
            width, height = img.size
            lines = []
            for y in range(height):
                row = []
                for x in range(width):
                    pixel = img.getpixel((x, y))
                    if isinstance(pixel, tuple):
                        r, g, b = pixel[:3]
                    else:
                        r = g = b = float(pixel)
                    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                    row.append(palette[min(len(palette) - 1, int(lum * (len(palette) - 1)))])
                lines.append("".join(row))
            return "\n".join(lines) if lines else "Sin cover"

    def _get_cover_status_widget(self) -> Optional[Static]:
        try:
            return self.query_one("#cover-status", Static)
        except Exception:
            return None

    def _update_cover_widget(self, data: bytes) -> None:
        status = self._get_cover_status_widget()
        try:
            image = PILImage.open(io.BytesIO(data))
            image.load()
        except Exception as exc:  # noqa: BLE001
            if status:
                status.update(f"Cover error: {exc}")
            self._set_status(f"Cover error: {exc}")
            return

        try:
            cover = self.query_one("#cover", TImage)
            cover.image = image
            if status:
                status.update("")
        except Exception as exc:
            message = None
            if status:
                try:
                    message = self._pixelate_to_text(data)
                except Exception as inner_exc:  # noqa: BLE001
                    message = f"Cover error: {inner_exc}"
                status.update(message)
            self._set_status(f"Cover error: {exc}")

    def _reset_cover(self) -> None:
        try:
            cover = self.query_one("#cover", TImage)
            cover.image = None
        except Exception:
            pass
        status = self._get_cover_status_widget()
        if status:
            status.update("Sin cover")
