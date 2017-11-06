from django.test import TestCase

from catracking import core


class TrackerTest(TestCase):

    class MyAbstractTracker(core.Tracker):
        pass

    class MyTracker(core.Tracker):

        def __init__(self):
            pass

        def send(self):
            pass

    def setUp(self):
        self.tracker = self.MyTracker()

    def test_init(self):
        pass
