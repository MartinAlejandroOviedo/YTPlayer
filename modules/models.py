from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    artist: str
    album: str
    duration: str
    video_id: str
    thumbnail_url: str

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}" if self.video_id else ""
