from typing import List
from extract.youtube.youtube_base_extractor import YouTubeBaseExtractor
from extract.youtube.VideoItem import VideoItem


class YouTubeVideosExtractor(YouTubeBaseExtractor):
    def __init__(self, file_id: str, video_ids: List[str]):
        """
        Initialize YouTubeExtractor for a specific channel.

        Args:
            username: YouTube channel username (e.g. "@channelname")
        """
        super().__init__(file_id)
        self.video_ids = video_ids

    def extract(self) -> None:
        video_item_stream = self.start_stream(VideoItem, identifier=self.file_id)

        for video_id in self.video_ids:
            video = self.fetch_video(video_id)
            self.stream_item(video, video_item_stream)

        self.end_stream(video_item_stream)


class YouTubePlaylistExtractor(YouTubeBaseExtractor):
    def __init__(self, file_id: str, playlist_id: str):
        super().__init__(file_id)
        self.playlist_id = playlist_id

    def extract(self) -> None:
        self.fetch_videos_for_playlist(self.playlist_id)
