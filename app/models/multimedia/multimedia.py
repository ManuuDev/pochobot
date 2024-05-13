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
