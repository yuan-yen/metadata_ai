import humming_bird as hb
import time

manager = hb.VideoDownloadManager(
    metadata_file='downloads/metadata.parquet',
    delay_time = 180
)
channels = [
    'https://www.youtube.com/@WhiteHouse',
    "https://www.youtube.com/@FoxBusiness/",
    'https://www.youtube.com/@FoxNews',
    'https://www.youtube.com/@ForbesBreakingNews',
    'https://www.youtube.com/@NBCNews',
    'https://www.youtube.com/@BloombergPodcasts',
    'https://www.youtube.com/@AssociatedPress',
    'https://www.youtube.com/@SkyNews',
    'https://www.youtube.com/@livenowfox',
    'https://www.youtube.com/@CNBCtelevision',
    'https://www.youtube.com/@NewsNation',
    'https://www.youtube.com/@CSPAN',
]

while True:
    manager.process_channels(channels, max_results=10)
    time.sleep(60)
