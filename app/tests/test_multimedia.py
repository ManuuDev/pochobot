import unittest

from app.Multimedia import Multimedia


class MultimediaTests(unittest.TestCase):
    
    def test_add_multimedia_to_queue(self):
        multimediaObject = Multimedia.multimedia_factory({}, url='url', typo='song')
        Multimedia.add_multimedia_to_queue(multimediaObject)
        self.assertEqual(len(Multimedia.youtubeQueue), 1)

    def test_clear_queue_test(self):
        multimediaObject = Multimedia.multimedia_factory({}, url='url', typo='song')
        Multimedia.add_multimedia_to_queue(multimediaObject)
        Multimedia.clean_queue()
        self.assertEqual(len(Multimedia.youtubeQueue), 0)
