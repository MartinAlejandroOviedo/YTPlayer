import json
import os
from typing import List, Optional
from urllib.parse import quote_plus
from urllib.request import urlopen

from ytmusicapi import YTMusic

from modules.models import SearchResult


class YouTubeMusicClient:
    def __init__(self, cookies_path: Optional[str] = None) -> None:
        """
        Inicializa YTMusic. Si hay cookies disponibles (parametro o env YTMUSIC_COOKIES / YTMUSIC_COOKIE_FILE),
        las usa para mejorar resultados (incl. letras). Si fallan, cae a modo sin auth.
        """
        self._yt = self._init_ytmusic(cookies_path)

    @staticmethod
    def _init_ytmusic(cookies_path: Optional[str]) -> YTMusic:
        # Orden de prioridad: parametro -> env YTMUSIC_COOKIES -> env YTMUSIC_COOKIE_FILE -> fallback sin cookies.
        candidates = [cookies_path, os.environ.get("YTMUSIC_COOKIES"), os.environ.get("YTMUSIC_COOKIE_FILE")]
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                try:
                    return YTMusic(candidate)
                except Exception:
                    continue
        # Fallback sin cookies
        return YTMusic()

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

    def get_song_lyrics(self, video_id: str, title: Optional[str] = None, artist: Optional[str] = None) -> str | None:
        """Devuelve letra desde YouTube Music, con fallback a API publica si es necesario."""
        # Primero intentar con YouTube Music.
        lyrics = self._get_ytm_lyrics(video_id)
        if lyrics:
            return lyrics
        # Fallback publico si tenemos artista y titulo.
        if title and artist:
            fallback = self._get_public_lyrics(title, artist)
            if fallback:
                return fallback
        return None

    def _get_ytm_lyrics(self, video_id: str) -> str | None:
        if not video_id:
            return None
        try:
            watch = self._yt.get_watch_playlist(video_id)
            lyrics_data = watch.get("lyrics") if isinstance(watch, dict) else None
            browse_id = lyrics_data.get("browseId") if isinstance(lyrics_data, dict) else None
            if not browse_id:
                return None
            lyrics_payload = self._yt.get_lyrics(browse_id)
            if isinstance(lyrics_payload, dict):
                return lyrics_payload.get("lyrics")
        except Exception:
            return None
        return None

    def _get_public_lyrics(self, title: str, artist: str) -> str | None:
        """Consulta una API publica (lyrist.vercel.app) para obtener letras."""
        try:
            url = f"https://lyrist.vercel.app/api/lyrics/{quote_plus(artist)}/{quote_plus(title)}"
            with urlopen(url, timeout=8) as resp:
                if resp.status != 200:
                    return None
                data = json.loads(resp.read().decode("utf-8", "ignore"))
            if isinstance(data, dict):
                text = data.get("lyrics")
                if text:
                    return text
        except Exception:
            return None
        return None
