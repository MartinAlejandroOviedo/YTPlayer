from typing import List

from ytmusicapi import YTMusic

from modules.models import SearchResult


class YouTubeMusicClient:
    def __init__(self) -> None:
        self._yt = YTMusic()

    def search_songs(self, query: str, limit: int = 20) -> List[SearchResult]:
        raw_results = self._yt.search(query, filter="songs", limit=limit)
        parsed: List[SearchResult] = []
        for item in raw_results:
            title = item.get("title") or "Sin titulo"
            artists = item.get("artists") or []
            artist = ", ".join(a.get("name", "?") for a in artists) if artists else "-"
            album_info = item.get("album") or {}
            album = album_info.get("name") or "-"
            duration = item.get("duration") or "-"
            video_id = item.get("videoId") or ""
            thumbs = item.get("thumbnails") or []
            thumb_url = ""
            if isinstance(thumbs, list) and thumbs:
                # tomar el de mayor resolucion (ultimo)
                thumb_url = thumbs[-1].get("url", "") or thumbs[0].get("url", "")
            parsed.append(SearchResult(title, artist, album, duration, video_id, thumb_url))
        return parsed
