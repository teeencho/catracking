import mock

from collections import OrderedDict
from time import time

from django.test import (
    TestCase,
    override_settings)

from catracking.ga import core


class GoogleAnalyticsTrackerTest(TestCase):

    def setUp(self):
        self.request = mock.MagicMock()
        self.tracker = core.GoogleAnalyticsTracker(self.request)

    def test_init(self):
        self.assertEquals('ga', self.tracker.IDENT)
        self.assertEquals(
            'https://www.google-analytics.com/collect', self.tracker.ENDPOINT)
        self.assertEquals(self.request, self.tracker.request)
        self.assertEquals([], self.tracker.hits)
        self.assertEquals(None, self.tracker._root_chunk)

    @override_settings(TRACKERS={'ga': {'DOCUMENT_HOSTNAME': 'www.ca.com'}})
    def test_generate_ga_cookie_www(self):
        cookie = core.GoogleAnalyticsTracker.generate_ga_cookie()
        prefix, sections, random_str, timestamp = cookie.split('.')
        self.assertEquals('GA1', prefix)
        self.assertEquals('2', sections)
        self.assertTrue(int(random_str) < 2147483647)
        self.assertTrue(timestamp <= str(int(time())))

    @override_settings(TRACKERS={'ga': {'DOCUMENT_HOSTNAME': 'ca.com'}})
    def test_generate_ga_cookie_no_www(self):
        cookie = core.GoogleAnalyticsTracker.generate_ga_cookie()
        prefix, sections, random_str, timestamp = cookie.split('.')
        self.assertEquals('GA1', prefix)
        self.assertEquals('2', sections)
        self.assertTrue(int(random_str) < 2147483647)
        self.assertTrue(timestamp <= str(int(time())))

    @override_settings(TRACKERS={'ga': {'DOCUMENT_HOSTNAME': 'mt.ca.com'}})
    def test_generate_ga_cookie_subdomain(self):
        cookie = core.GoogleAnalyticsTracker.generate_ga_cookie()
        prefix, sections, random_str, timestamp = cookie.split('.')
        self.assertEquals('GA1', prefix)
        self.assertEquals('3', sections)
        self.assertTrue(int(random_str) < 2147483647)
        self.assertTrue(timestamp <= str(int(time())))

    @override_settings(TRACKERS={'ga': {'DOCUMENT_HOSTNAME': 'mt.ca.com.br'}})
    def test_generate_ga_cookie_impossible_but_possible(self):
        cookie = core.GoogleAnalyticsTracker.generate_ga_cookie()
        prefix, sections, random_str, timestamp = cookie.split('.')
        self.assertEquals('GA1', prefix)
        self.assertEquals('4', sections)
        self.assertTrue(int(random_str) < 2147483647)
        self.assertTrue(timestamp <= str(int(time())))

    @mock.patch('catracking.ga.core.RootHitChunk.__new__')
    def test_get_root_chunk(self, p_init):
        root_chunk = self.tracker.get_root_chunk()
        p_init.assert_called_once()
        self.assertTrue(bool(root_chunk))

    @mock.patch('catracking.ga.core.RootHitChunk.__init__')
    def test_get_root_chunk_already_instantiated(self, p_init):
        self.tracker._root_chunk = 1
        root_chunk = self.tracker.get_root_chunk()
        p_init.assert_not_called()
        self.assertEquals(1, root_chunk)

    def test_new_event(self):
        event = self.tracker.new_event('category', 'action', 'label')
        self.assertIn(event, self.tracker.hits)
        self.assertIsInstance(event, core.EventHitChunk)

    def test_new_pageview(self):
        with self.assertRaises(NotImplementedError):
            self.tracker.new_pageview()

    @mock.patch('catracking.ga.core.BaseMeasurementProtocolHit.copy')
    @mock.patch('catracking.ga.core.BaseMeasurementProtocolHit.compile')
    def test_compile_hits(self, p_compile, p_copy):
        p_copy.return_value = core.BaseMeasurementProtocolHit()
        p_compile.return_value = core.BaseMeasurementProtocolHit()
        self.tracker._root_chunk = core.BaseMeasurementProtocolHit({1: 2})
        self.tracker.hits = [core.BaseMeasurementProtocolHit()] * 2
        self.tracker.compile_hits()
        self.assertEquals([{}, {}], self.tracker.hits)

    @mock.patch('catracking.core.Tracker.send')
    @mock.patch('random.randint')
    def test_send(self, p_randint, p_send):
        p_randint.return_value = 1
        self.tracker.hits = [core.BaseMeasurementProtocolHit()] * 2
        with mock.patch.object(self.tracker, 'compile_hits') as p_compile_hits:
            self.tracker.send()
            p_compile_hits.assert_called_once()
            p_send.assert_called_with(['z=1', 'z=1'])


class BaseMeasurementProtocolHitTest(TestCase):

    def setUp(self):
        self.hit = core.BaseMeasurementProtocolHit()

    def test_init(self):
        self.assertIsInstance(self.hit, OrderedDict)

    def test_add(self):
        chunk = {'a': 1}
        self.assertEquals(OrderedDict({'a': 1}), self.hit + chunk)

    def test_add_existing_key(self):
        self.hit['a'] = 2
        chunk = {'a': 1}
        self.assertEquals(OrderedDict({'a': 1}), self.hit + chunk)

    def test_iadd(self):
        chunk = {'a': 1}
        self.hit += chunk
        self.assertEquals(OrderedDict({'a': 1}), self.hit)

    def test_iadd_existing_key(self):
        self.hit['a'] = 2
        chunk = {'a': 1}
        self.hit += chunk
        self.assertEquals(OrderedDict({'a': 1}), self.hit)

    def test_setitem(self):
        self.hit['a'] = 1
        self.assertEquals(OrderedDict({'a': 1}), self.hit)

    def test_setitem_empty_string(self):
        self.hit['a'] = ''
        self.assertEquals(OrderedDict({}), self.hit)

    def test_setitem_none(self):
        self.hit['a'] = None
        self.assertEquals(OrderedDict({}), self.hit)

    def test_copy(self):
        self.hit['a'] = 1
        self.hit['b'] = 'a'
        self.hit['d'] = ''
        self.hit['c'] = None
        self.assertEquals(
            core.BaseMeasurementProtocolHit([('a', 1), ('b', 'a')]),
            self.hit.copy())

    @mock.patch('random.randint')
    def test_encoded_url(self, p_randint):
        p_randint.return_value = 2
        self.hit['a'] = 1
        self.hit['b'] = 'a'
        self.assertEquals('a=1&b=a&z=2', self.hit.encoded_url)

    @mock.patch('random.randint')
    def test_encoded_url_no_value(self, p_randint):
        p_randint.return_value = 2
        self.assertEquals('z=2', self.hit.encoded_url)

    def test_compile(self):
        self.assertEquals(self.hit, self.hit.compile())
