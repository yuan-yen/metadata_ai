import os
import subprocess
import pandas as pd
import time
from typing import List, Dict
from datetime import datetime

class VideoDownloadManager:
    def __init__(
        self,
        cookies_path: str = "cookies.txt",
        output_dir: str = "downloads",
        metadata_file: str = "metadata.parquet",
        delay_time: float = 1.0,
        timeout_time: float = 300.0,  # 5 minutes
    ):
        self.cookies_path = cookies_path
        self.output_dir = output_dir
        self.metadata_file = metadata_file
        self.delay_time = delay_time
        self.timeout_time = timeout_time
        os.makedirs(self.output_dir, exist_ok=True)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> pd.DataFrame:
        if os.path.exists(self.metadata_file):
            return pd.read_parquet(self.metadata_file)
        else:
            return pd.DataFrame(columns=[
                "channel_title", "video_id", "video_title", "video_url",
                "upload_date", "audio_path"
            ])

    def _save_metadata(self):
        self.metadata.to_parquet(self.metadata_file, index=False)

    def _get_latest_videos(self, url: str, max_results: int) -> List[Dict]:
        if not url.rstrip("/").endswith("/videos"):
            url = url.rstrip("/") + "/videos"

        cmd = [
            "yt-dlp",
            "--cookies", self.cookies_path,
            "--flat-playlist",
            f"--playlist-end={max_results}",
            "--print", "%(id)s\t%(title)s",
            url
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")

        videos = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.strip().split("\t", 1)
                if len(parts) == 2:
                    video_id, title = parts
                    videos.append({
                        "id": video_id,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
        return videos

    def _is_downloaded(self, video_id: str) -> bool:
        return video_id in self.metadata["video_id"].values

    def _download_audio(self, video: Dict, channel_name: str) -> str:
        channel_folder = os.path.join(self.output_dir, channel_name)
        os.makedirs(channel_folder, exist_ok=True)

        output_template = os.path.join(channel_folder, f"%(id)s.%(ext)s")
        cmd = [
            "yt-dlp",
            "--cookies", self.cookies_path,
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            "-o", output_template,
            video["url"]
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=self.timeout_time
        )
        if result.returncode != 0:
            raise RuntimeError(f"Download failed: {result.stderr.strip()}")

        return os.path.join(channel_folder, f"{video['id']}.mp3")

    def process_channels(self, channel_urls: List[str], max_results: int = 5):
        for url in channel_urls:
            parts = url.rstrip("/").split("/")
            channel_part = parts[-1] if parts[-1] != "videos" else parts[-2]
            channel_name = channel_part.replace("@", "")

            print(f"Checking channel: {channel_name}")
            try:
                videos = self._get_latest_videos(url, max_results)
            except Exception as e:
                print(f"Failed to fetch videos from {url}: {e}")
                continue

            for video in videos:
                if self._is_downloaded(video["id"]):
                    print(f"Skipping already downloaded video: {video['title']}")
                    continue

                print(f"Downloading: {video['title']}")
                try:
                    audio_path = self._download_audio(video, channel_name)
                except subprocess.TimeoutExpired:
                    print(f"Timeout: Download took more than {self.timeout_time} seconds: {video['url']}")
                    continue
                except Exception as e:
                    print(f"Failed to download {video['url']}: {e}")
                    continue

                self.metadata = pd.concat([
                    self.metadata,
                    pd.DataFrame([{
                        "channel_title": channel_name,
                        "video_id": video["id"],
                        "video_title": video["title"],
                        "video_url": video["url"],
                        "upload_date": datetime.now().isoformat(),
                        "audio_path": audio_path
                    }])
                ], ignore_index=True)
                self._save_metadata()

                # Delay before processing the next video
                time.sleep(self.delay_time)