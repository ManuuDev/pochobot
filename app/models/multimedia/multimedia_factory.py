from app.models.multimedia.playlist import Playlist
from app.models.multimedia.radio import Radio
from app.models.multimedia.song import Song
from app.models.multimedia.youtube_live import YoutubeLive


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
