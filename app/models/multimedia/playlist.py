from app.models.multimedia.multimedia import Multimedia


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
