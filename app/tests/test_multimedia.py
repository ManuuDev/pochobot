import unittest

from app.core import multimedia_manager


class MultimediaTests(unittest.TestCase):
    
    def test_add_multimedia_to_queue(self):
        multimediaObject = multimedia_manager.multimedia_factory({}, url='url', typo='song')
        multimedia_manager.add_multimedia_to_queue(multimediaObject)
        self.assertEqual(len(multimedia_manager.youtubeQueue), 1)

    def test_clear_queue_test(self):
        multimediaObject = multimedia_manager.multimedia_factory({}, url='url', typo='song')
        multimedia_manager.add_multimedia_to_queue(multimediaObject)
        multimedia_manager.clean_queue()
        self.assertEqual(len(multimedia_manager.youtubeQueue), 0)
