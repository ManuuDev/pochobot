import datetime as datetime
from discord import FFmpegOpusAudio
from ..System.Utils import get_radio_from_value


def multimedia_factory(ctx, url=None, info=None, typo=None):
    if typo:

        if typo == 'song':
            return Song(ctx, url=url, info=info)
        elif typo == 'liveStream':
            return YoutubeLive(ctx, url=url, info=info)
        elif typo == 'playlist':
            return Playlist(ctx, url=url, info=info)
        elif typo == 'radio':
            return Radio(ctx, url, True)
        else:
            print('Error: El tipo no existe')

    elif info:
        try:
            if info.get('_type') == 'playlist':
                return Playlist(ctx, url=url, info=info)
        except:
            pass

        try:
            if info.get('is_live'):
                return YoutubeLive(ctx, url=url, info=info)
        except:
            pass

        return Song(ctx, url=url, info=info)
    else:
        print('Error al crear objeto multimedia')


class Multimedia:
    beforeArgs = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
    processed: bool = False
    ctx: object
    title: str
    typo: str
    url: str
    duration: str
    audioSource: object

    def fill_fields(self, info):
        pass

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__"):
                yield attr


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


class Playlist(Multimedia):
    tracks: int

    def __init__(self, ctx, url=None, info=None):
        self.ctx = ctx
        self.url = url

        if info:
            self.fill_fields(info)

    def fill_fields(self, info):
        self.title = info.get('title')
        self.typo = info.get('_type')
        self.duration = 'playlist'
        self.tracks = len(info.get('entries'))


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
        self.audioSource = FFmpegOpusAudio(self.url,
                                           before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')
        self.processed = True


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
