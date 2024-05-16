from discord import FFmpegOpusAudio
from app.system.utils import get_radio_from_value
from app.models.multimedia.multimedia import Multimedia


class Radio(Multimedia):
    def __init__(self, ctx, url, process=False):
        self.ctx = ctx
        self.url = url
        self.title = get_radio_from_value(url)
        self.typo = 'radio'
        self.duration: str = 'live stream'
        if process:
            self.fill_fields()

    def fill_fields(self, info=None):
        self.audioSource = FFmpegOpusAudio(self.url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        self.processed = True
