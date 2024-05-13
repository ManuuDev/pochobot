import datetime

from discord import FFmpegOpusAudio
from app.models.multimedia.multimedia import Multimedia


class Song(Multimedia):
    def __init__(self, ctx, url=None, info=None):
        self.ctx = ctx
        self.url = url

        if info:
            self.fill_fields(info)

    def fill_fields(self, info):
        self.title = info.get('title')
        self.typo = 'song'
        self.duration = str(datetime.timedelta(seconds=info.get('duration')))
        formats = info['formats']
        #Extracts the url of the streaming of format 48000 quality 1
        #Or 44100 if not found
        format48kq1 = [x for x in formats if x.get('format_id') in ['600','251']][0]
        url = format48kq1['url']
        self.audioSource = FFmpegOpusAudio(url, before_options=self.beforeArgs)
        self.processed = True