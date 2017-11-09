import mock

from collections import OrderedDict
from time import time

from django.test import (
    TestCase,
    override_settings)

from catracking.ga import (
    core,
    parameters,
    metrics,
    events)


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
        event = self.tracker.new_event(
            events.EVENT_CATEGORY_VERIFIED_LEAD,
            'frontpoint',
            events.EVENT_LABEL_CLICK)
        self.assertIn(event, self.tracker.hits)
        self.assertIsInstance(event, core.EventHitChunk)

    def test_new_pageview(self):
        with self.assertRaises(NotImplementedError):
            self.tracker.new_pageview()

    def test_compile_hits(self):
        self.tracker._root_chunk = core.BaseMeasurementProtocolHit({1: 2})
        self.tracker.hits = [core.BaseMeasurementProtocolHit({2: 3})] * 2
        self.tracker.compile_hits()
        self.assertEquals([{1: 2, 2: 3}, {1: 2, 2: 3}], self.tracker.hits)

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


@override_settings(
    TRACKERS={'ga': {'PROPERTY': 'XXX-YY', 'DOCUMENT_HOSTNAME': 'www.ca.com'}})
class RootHitChunkTest(TestCase):

    def setUp(self):
        self.request = mock.MagicMock()
        self.request.session = {}
        self.request.META = {'HTTP_USER_AGENT': 'Chrome'}
        self.request.COOKIES = {'_ga2017': 'GA1.2.12345.12345'}
        self.request.user.pk = 999
        self.hit = core.RootHitChunk(self.request)

    def test_init(self):
        self.assertEquals(self.request, self.hit.request)
        self.assertEquals(1, self.hit[parameters.VERSION])
        self.assertEquals('XXX-YY', self.hit[parameters.TRACKING_ID])
        self.assertEquals('12345.12345', self.hit[parameters.CLIENT_ID])
        self.assertEquals(999, self.hit[parameters.USER_ID])
        self.assertEquals('Chrome', self.hit[parameters.USER_AGENT])
        self.assertEquals('www.ca.com', self.hit[parameters.DOCUMENT_HOSTNAME])
        self.assertEquals('12345.12345', self.hit[parameters.CLIENT_ID])

    def test_ga_property(self):
        self.assertEquals('XXX-YY', self.hit.ga_property)

    def test_document_hostname(self):
        self.assertEquals('www.ca.com', self.hit.document_hostname)

    def test_client_id_cookie_in_session(self):
        self.hit.request.session = {'ga_cookie': 'GA1.2.99999.99999'}
        self.assertEquals('99999.99999', self.hit.client_id)

    def test_client_id_cookie_not_in_session_but_in_cookies(self):
        self.hit.request.session = {}
        self.hit.request.COOKIES = {'_ga2017': 'GA1.2.12345.12345'}
        self.assertEquals('12345.12345', self.hit.client_id)

    def test_client_id_cookie_not_in_session_and_not_in_cookies(self):
        self.hit.request.session = {}
        self.hit.request.COOKIES = {}
        self.assertEquals('', self.hit.client_id)

    def test_user_id(self):
        self.assertEquals(999, self.hit.user_id)

    def test_user_id_no_user(self):
        self.request.user = None
        self.hit = core.RootHitChunk(self.request)
        self.assertEquals(0, self.hit.user_id)


class HitProductsMixinTest(TestCase):

    class Hit(core.HitProductsMixin, core.BaseMeasurementProtocolHit):
        pass

    def setUp(self):
        self.hit = self.Hit()

    def test_init(self):
        self.assertIsInstance(self.hit, core.BaseMeasurementProtocolHit)
        self.assertEquals(None, self.hit._transaction)
        self.assertEquals([], self.hit._products)

    def test_new_transaction(self):
        transaction = self.hit.new_transaction(10, 'affiliation', 10.0)
        self.assertEquals(transaction, self.hit._transaction)

    def test_set_product_action(self):
        self.hit.set_product_action('click')
        self.assertEquals('click', self.hit[parameters.PRODUCT_ACTION])

    def test_new_product(self):
        product = self.hit.new_product(10, 'name', 'cat', 'brand', 10.0, 1)
        self.assertEquals(product, self.hit._products[0])
        self.assertEquals('pr1id', list(self.hit._products[0].keys())[0])

    def test_new_product_second(self):
        self.hit.new_product(10, 'name', 'cat', 'brand', 10.0, 1)
        product = self.hit.new_product(11, 'name', 'cat', 'brand', 10.0, 1)
        self.assertEquals(product, self.hit._products[1])
        self.assertEquals('pr2id', list(self.hit._products[1].keys())[0])

    def test_compile_without_transaction(self):
        self.hit.compile()
        self.hit[metrics.CM12_HS_SECONDS_ENGAGED] = 1
        self.assertNotIn(parameters.TRANSACTION_ID, self.hit)
        self.assertIn(metrics.CM12_HS_SECONDS_ENGAGED, self.hit)

    def test_compile_with_transaction(self):
        self.hit.new_transaction(10, 'affiliation', 10.0)
        self.hit.compile()
        self.assertIn(parameters.TRANSACTION_ID, self.hit)
        self.assertIn(parameters.TRANSACTION_AFFILIATION, self.hit)
        self.assertIn(parameters.TRANSACTION_REVENUE, self.hit)
        self.assertNotIn('pr1id', self.hit)

    def test_compile_with_products(self):
        self.hit.new_transaction(10, 'affiliation', 10.0)
        self.hit.new_product(10, 'name', 'cat', 'brand', 10.0, 1)
        self.hit.new_product(11, 'name', 'cat', 'brand', 10.0, 1)
        self.hit.compile()
        self.assertIn(parameters.TRANSACTION_ID, self.hit)
        self.assertIn(parameters.TRANSACTION_AFFILIATION, self.hit)
        self.assertIn(parameters.TRANSACTION_REVENUE, self.hit)
        self.assertIn('pr1id', self.hit)
        self.assertIn('pr1nm', self.hit)
        self.assertIn('pr1ca', self.hit)
        self.assertIn('pr1br', self.hit)
        self.assertIn('pr2id', self.hit)
        self.assertIn('pr2nm', self.hit)
        self.assertIn('pr2ca', self.hit)
        self.assertIn('pr2br', self.hit)


class EventHitChunkTest(TestCase):

    def setUp(self):
        self.hit = core.EventHitChunk('category', 'action', 'label')

    def test_init(self):
        self.assertIsInstance(self.hit, core.BaseMeasurementProtocolHit)
        self.assertEquals('event', self.hit[parameters.HIT_TYPE])
        self.assertEquals('category', self.hit[parameters.EVENT_CATEGORY])
        self.assertEquals('action', self.hit[parameters.EVENT_ACTION])
        self.assertEquals('label', self.hit[parameters.EVENT_LABEL])
        self.assertEquals(0, self.hit[parameters.EVENT_VALUE])
        self.assertEquals(0, self.hit[parameters.EVENT_NON_INTERACTIVE])


class TransactionHitChunkTest(TestCase):

    def setUp(self):
        self.hit = core.TransactionHitChunk(1, 'affiliation', 10.0)

    def test_init(self):
        self.assertIsInstance(self.hit, core.BaseMeasurementProtocolHit)
        self.assertEquals(1, self.hit[parameters.TRANSACTION_ID])
        self.assertEquals(
            'affiliation', self.hit[parameters.TRANSACTION_AFFILIATION])
        self.assertEquals(10.0, self.hit[parameters.TRANSACTION_REVENUE])


class ProductHitChunkTest(TestCase):

    def setUp(self):
        self.hit = core.ProductHitChunk(
            1, 10, 'name', 'category', 'brand', 10.0, 1)

    def test_init(self):
        self.assertEquals(1, self.hit.index)
        self.assertEquals(10, self.hit['pr1id'])
        self.assertEquals('name', self.hit['pr1nm'])
        self.assertEquals('category', self.hit['pr1ca'])
        self.assertEquals('brand', self.hit['pr1br'])
        self.assertEquals(10.0, self.hit['pr1pr'])
        self.assertEquals(1, self.hit['pr1qt'])

    def test_set_item(self):
        self.hit['a'] = 1
        self.assertEquals('pr1a', list(self.hit.keys())[-1])

    def test_set_item_2(self):
        self.hit = core.ProductHitChunk(2, 10)
        self.hit['a'] = 1
        self.assertEquals('pr2a', list(self.hit.keys())[-1])
