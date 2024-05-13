from discord import FFmpegOpusAudio
from app.models.multimedia.multimedia import Multimedia


class YoutubeLive(Multimedia):
    def __init__(self, ctx, url=None, info=None):
        self.ctx = ctx
        self.url = url

        if info:
            self.fill_fields(info)

    def fill_fields(self, info):
        self.title = info.get('title')
        self.typo = 'live'
        self.duration = 'live stream'
        formats = info['formats']
        #Extracts the url of the streaming of format mp4 854p
        formatmp4854p = [x for x in formats if x.get('format_id') == '94'][0]
        url = formatmp4854p['url']
        self.audioSource = FFmpegOpusAudio(url, before_options=self.beforeArgs)
        self.processed = True
