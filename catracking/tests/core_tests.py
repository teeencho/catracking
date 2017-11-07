import mock

from django.test import (
    TestCase,
    override_settings)

from catracking import core


class TrackerTest(TestCase):

    class MyAbstractTracker(core.Tracker):
        pass

    class MyTracker(core.Tracker):

        IDENT = 'mytracker'
        ENDPOINT = 'https://my.tracker.com'

        def __init__(self):
            pass

        def send(self, payload_bucket):
            super(TrackerTest.MyTracker, self).send(payload_bucket)

    def setUp(self):
        self.tracker = self.MyTracker()

    def test_abstract_init(self):
        with self.assertRaises(TypeError):
            self.MyAbstractTracker()

    @override_settings(TRACKERS={'ga': {}})
    def test_is_active_tracker_not_configured(self):
        self.assertFalse(self.MyTracker.is_active())

    @override_settings(TRACKERS={'mytracker': {}})
    def test_is_active_configured(self):
        self.assertTrue(self.MyTracker.is_active())

    def test_base_settings_without_trackers(self):
        with self.assertRaises(core.TrackerNotConfiguredError):
            self.MyTracker.base_settings()

    @override_settings(TRACKERS={'ga': {}})
    def test_base_settings_without_specific_tracker(self):
        with self.assertRaises(core.TrackerNotConfiguredError):
            self.MyTracker.base_settings()

    @override_settings(TRACKERS={'mytracker': {'valid_key': 1}})
    def test_settings_without_key(self):
        with self.assertRaises(core.MissingTrackerConfigurationError):
            self.MyTracker.settings('invalid_key')

    @override_settings(TRACKERS={'mytracker': {'valid_key': 1}})
    def test_setttings_with_key(self):
        self.assertEquals(1, self.MyTracker.settings('valid_key'))

    @mock.patch('catracking.core.SendTrackingDataTask.delay')
    def test_send(self, p_send_tracking_data_task):
        self.tracker.send([1])
        p_send_tracking_data_task.assert_called_with(
            'mytracker', 'https://my.tracker.com', 1)

    @mock.patch('catracking.core.SendTrackingDataTask.delay')
    def test_send_multiple_payloads(self, p_send_tracking_data_task):
        self.tracker.send([1, 2, 3])
        p_send_tracking_data_task.assert_has_calls([
            mock.call('mytracker', 'https://my.tracker.com', 1),
            mock.call('mytracker', 'https://my.tracker.com', 2),
            mock.call('mytracker', 'https://my.tracker.com', 3)
        ])
