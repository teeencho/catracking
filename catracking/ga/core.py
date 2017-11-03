import catracking.ga.parameters as parameters
import random
import time
import uuid

from collections import OrderedDict
from urllib import urlencode

from django.utils.functional import cached_property

from catracking.core import Tracker
from catracking.ga.dimensions import CD25_US_GA_CLIENT_ID


class GoogleAnalyticsTracker(Tracker):
    """
    Creates a Google Analytics Tracker.
    Handles every hit creation and re-usage of common data, for each single
    request, the base structure of a hit should be the same.
    """
    IDENT = 'ga'
    ENDPOINT = 'https://www.google-analytics.com/collect'

    def __init__(self, request):
        super(GoogleAnalyticsTracker, self).__init__()
        self.request = request
        self.hits = []
        self._root_chunk = None

    @staticmethod
    def generate_ga_client_id():
        """
        Generates a new random id to be used as client id if one is not
        provided by Google Analytics.
        """
        random_string = str(uuid.uuid4().int % 2147483647)
        timestamp = str(int(time()))
        return 'GA1.1.{0}'.format('.'.join([random_string, timestamp]))

    def get_root_chunk(self):
        if not self._root_chunk:
            self._root_chunk = RootHitChunk(self.request)
        return self._root_chunk

    def new_event(self, category, action, label, value=0, non_interactive=1):
        """
        Creates a new event hit and appends it to the hits pool.
        A reference to the event hit is returned so it can be dynamically
        populated with custom data.
        """
        event = EventHitChunk(category, action, label, value, non_interactive)
        self.hits.append(event)
        return event

    def new_pageview(self):
        raise NotImplementedError('Pageview event is not implemented yet')

    def compile_hits(self):
        """
        Compiles all hits created in the tracker, generating a base hit
        structure for each of them, with all information contained in the
        root chunk, merged with the hit chunk itself.

        This is necessary because every hit can be dinamically updated after
        its creation, so we need to wait until the hit is fully completed
        before merging the data.
        """
        self.hits = [
            self.get_root_chunk().copy() + hit.compile() for hit in self.hits]

    def send(self):
        self.compile_hits()
        payload_bucket = [hit.encoded_url for hit in self.hits]
        super(GoogleAnalyticsTracker, self).send(payload_bucket)


class BaseMeasurementProtocolHit(OrderedDict):
    """
    Base for any hit chunk. Adds more functionality to an OrderedDict.
    """

    def __init__(self, *args, **kwargs):
        super(BaseMeasurementProtocolHit, self).__init__(*args, **kwargs)

    def __add__(self, chunk):
        """
        Additions to a hit chunk are literally an update call to its
        dictionary. Merging is possible with `c = a + b`.
        """
        self.update(chunk)
        return self

    def __iadd__(self, chunk):
        """
        Self additions to a hit chunk are literally an update call to its
        dictionary. Merging is possible with `a += b`.
        """
        self.update(chunk)
        return self

    def __setitem__(self, key, value):
        """
        If the value being added to the dictionary is either `None` or an
        empty string, the key should not exist.
        """
        if not (value is None or value == ''):
            super(BaseMeasurementProtocolHit, self).__setitem__(key, value)

    def copy(self):
        """
        When copying a hit chunk, the only thing that matters is its data, in
        other words, its `items()`. This function gracelly overrides the
        `OrderedDict` copy returning a base structure hit in any subclass
        that copy was called.
        """
        return BaseMeasurementProtocolHit(self.items())

    @property
    def encoded_url(self):
        """
        Returns the full encoded url for the hit.
        Cache buster parameter should be the last in the querystring.
        """
        self[parameters.CACHE_BUSTER] = random.randint(1, 100000)
        return urlencode(self)

    def compile(self):
        """
        Hit chunks should be compilable, but only a few of them will actually
        compile something. e.g.: chunks with `HitProductsMixin` need to compile
        transaction and products.
        """
        return self


class RootHitChunk(BaseMeasurementProtocolHit):
    """
    All information added to the root hit chunk is required and should be
    the same for every type of hit.
    """

    def __init__(self, request):
        super(RootHitChunk, self).__init__()
        self.request = request
        self[parameters.VERSION] = 1
        self[parameters.TRACKING_ID] = self.ga_property
        self[parameters.CLIENT_ID] = self.client_id
        if self.user_id:
            self[parameters.USER_ID] = self.user_id
        self[parameters.USER_AGENT] = self.request.META.get(
            'HTTP_USER_AGENT', '')
        self[parameters.DOCUMENT_HOSTNAME] = self.document_hostname
        self[CD25_US_GA_CLIENT_ID] = self.client_id

    @property
    def ga_property(self):
        """
        Google Analytics property should be equal to the specific property
        in our account that we are going to send the hits.
        Production and test/local environments currently have different ones.
        """
        return GoogleAnalyticsTracker.settings('PROPERTY')

    @property
    def document_hostname(self):
        """
        Document Hostname is used to identify from which host an event
        is coming from. In some cases GA does not bind an event to a session
        and if we don't specify the document hostname, we can't identify
        what application sent it.
        """
        return GoogleAnalyticsTracker.settings('DOCUMENT_HOSTNAME')

    @cached_property
    def client_id(self):
        """
        ID generated in Google Analytics for each client.
        A middleware should handle the creation of it in case Google Analytics
        was not loaded beforehand.
        If the middleware created the value, it will be available in the
        session as `ga_client_id`.

        Every hit should contain a client id, so it can be identified and
        included to a specific session.

        A `_ga2017` cookie real example: `GA1.1.809004643.1509480820` and
        in Measurement Protocol, we need to get rid of `GA1.1.`.
        """
        return self.request.session.get(
            'ga_client_id', None
        ) or '.'.join(self.request.COOKIES.get('_ga2017', '').split('.')[-2:])

    @cached_property
    def user_id(self):
        """
        Identifies the user in our database inside GA.
        If there's an user attached to the request, returns its pk.
        Non authenticated users will return either 0 or `None`.
        """
        try:
            return self.request.user.pk
        except AttributeError:
            return 0


class HitProductsMixin(object):
    """
    Used whenever a hit chunk is able to contain products.
    For example, a custom event or a pageview.
    """

    def __init__(self):
        super(HitProductsMixin, self).__init__()
        self._transaction = None
        self._products = []

    def new_transaction(self, id, affiliation=None, revenue=None):
        """
        Creates a transaction chunk and returns it, in case extra (not default)
        dimensions or metrics need to be added.
        """
        self._transaction = TransactionHitChunk(id, affiliation, revenue)
        return self._transaction

    def set_product_action(self, action):
        self[parameters.PRODUCT_ACTION] = action

    def new_product(self, id=None, name=None, category=None, brand=None,
                    price=None, quantity=None):
        """
        Creates a product chunk and returns it, in case extra (not default)
        dimensions or metrics need to be added.
        """
        index = len(self._products) + 1
        product = ProductHitChunk(
            index, id, name, category, brand, price, quantity)
        self._products.append(product)
        return product

    def compile(self):
        """
        Merges the transaction and products into the hit, new transaction or
        new products should not be added after this.
        """
        if self._transaction:
            self += self._transaction
        for product in self._products:
            self += product
        return self


class PageViewHitChunk(HitProductsMixin, BaseMeasurementProtocolHit):
    pass


class EventHitChunk(HitProductsMixin, BaseMeasurementProtocolHit):
    """
    Builds part of a hit, this should be merged to the base of the
    Measurement Protocol hit.

    Adds the base information required for an `event` hit type, any
    additional data can be appended to the object (custom dimensions, metrics)
    """

    def __init__(self, category, action, label, value=0, non_interactive=0):
        """
        Events are non interactive by default, using `non_interactive=0`
        makes it interactive and will affect the bounce rate data
        """
        super(EventHitChunk, self).__init__()
        self[parameters.HIT_TYPE] = parameters.HIT_TYPE_EVENT
        self[parameters.EVENT_CATEGORY] = category
        self[parameters.EVENT_ACTION] = action
        self[parameters.EVENT_LABEL] = label
        self[parameters.EVENT_VALUE] = value
        self[parameters.EVENT_NON_INTERACTIVE] = non_interactive


class TransactionHitChunk(BaseMeasurementProtocolHit):
    """
    Builds part of a hit, this should be merged to the base of the
    Measurement Protocol hit.

    Adds the information required for the `transaction` chunk in a hit.
    """

    def __init__(self, id, affiliation=None, revenue=None):
        super(TransactionHitChunk, self).__init__()
        self[parameters.TRANSACTION_ID] = id
        if affiliation:
            self[parameters.TRANSACTION_AFFILIATION] = affiliation
        if revenue:
            self[parameters.TRANSACTION_REVENUE] = revenue


class ProductHitChunk(BaseMeasurementProtocolHit):

    def __init__(self, index, id=None, name=None, category=None, brand=None,
                 price=None, quantity=None):
        super(ProductHitChunk, self).__init__()
        self.index = index
        self[parameters.PRODUCT_ID] = id
        self[parameters.PRODUCT_NAME] = name
        self[parameters.PRODUCT_CATEGORY] = category
        self[parameters.PRODUCT_BRAND] = brand
        self[parameters.PRODUCT_PRICE] = price
        self[parameters.PRODUCT_QUANTITY] = quantity

    def __setitem__(self, key, value):
        key = 'pr{0}{1}'.format(self.index, key)
        super(ProductHitChunk, self).__setitem__(key, value)
