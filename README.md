# catracking

This package is responsible for all the tracking considered "cross-application" in our codebase.
Currently, the only tracker implemented is for Google Analytics (Measurement Protocol)

## Configuration

Each tracker will have its own configuration dictionary, inside `TRACKERS`.
If the tracker is not configured and the middleware is being used, exceptions will be thrown.
The configuration parameters should vary according to which environment you are.

### GA

Ident: `ga`

Configuration parameters:
* PROPERTY: Google Analytics property
* DOCUMENT_HOSTNAME: Hostname of the application. e.g.: `consumeraffairs.com` or `matchingtool.consumeraffairs.com`
* COOKIE_DOMAIN: Domain for the `_ga2017` cookie. This only needs to be set if the application will use the `GoogleAnalyticsCookieMiddleware`.

Configuration example for a local environment:

```
TRACKERS = {
  'ga': {
      'PROPERTY': 'UA-12322096-14',
      'DOCUMENT_HOSTNAME': 'www.consumeraffairs.com'
  }
}
```

Configuration example for a local environment with the cookie middleware:

```
TRACKERS = {
  'ga': {
      'PROPERTY': 'UA-12322096-14',
      'DOCUMENT_HOSTNAME': 'matchingtool.consumeraffairs.com',
      'COOKIE_DOMAIN': '.consumeraffairs.com'
  }
}
```

Please note the `.` before `consumeraffairs.com` in the `COOKIE_DOMAIN`. That is necessary in order to make the cookie cross-domain.

## Middlewares

In order to have the trackers available for usage, the `TrackingMiddleware` needs to be added to your list of `MIDDLEWARE_CLASSES`. This middleware will attach every configured tracker into the `request` object.

```
MIDDLEWARE_CLASSES = (
    '...',
    'catracking.middleware.TrackingMiddleware'
)
```

Let's say you have configured your `ga` tracker and added the `TrackingMiddleware`, you could access the tracker object in a CBV like this:

```
class MyTrackingView(View):
    def dispatch(self):
        tracker = self.request.trackers.ga
```

### GA specific middlewares

#### `GoogleAnalyticsCookieMiddleware`

For GA, there is an optional middleware called `GoogleAnalyticsCookieMiddleware` that can be used in specific applications, depending on its requirements.

This middleware creates the `_ga2017` cookie if it is not yet present in the request and insert it into the response. So for example, let's say the application sends the `PageView` event from the back-end and does not include the `GA` snippet in the front-end, that's one of the cases this middleware would be set in place.

**IMPORTANT:** Include this middleware before the `TrackingMiddleware`.

## Usage

### GA

#### Creating a custom event

Events in Google Analytics are represented by a `cateogory`, an `action`, a
`label`, a `value` and if they are `non-interactive`. Custom dimensions, custom
metrics, products and transactions can also be added to them.

With this API, creating an event in a view is pretty much straight forward, so
let's get into some examples.

Definition:
```
def new_event(self, category, action, label, value=0, non_interactive=1)
```

Examples:

```
def some_view_hook(self):

    event = self.request.trackers.ga.new_event(
        'brand interaction', 'submit lead', 'Frontpoint')

    interactive_event = self.request.trackers.ga.new_event(
        'brand interaction', 'submit lead', 'Frontpoint', non_interactive=0)

    value_event = self.request.trackers.ga.new_event(
        'brand interaction', 'submit lead', 'Frontpoint', 1)
```

Adding custom dimensions and metrics:

```
from catracking.ga import (
    dimensions,
    metrics)

def some_view_hook(self):

    event = self.request.trackers.ga.new_event(
        'brand interaction', 'submit lead', 'Frontpoint')

    event[dimensions.CD50_HS_BRAND_ID] = 1234
    event[metrics.CM37_HS_EMAIL_OPEN] = 0
```

Adding a transaction to the event:

Definition:
```
def new_transaction(self, id, affiliation=None, revenue=None)
```

Examples:

```
def some_view_hook(self):

    event = self.request.trackers.ga.new_event(
        'verified lead', 'Frontpoint', 'click')

    event.new_transaction(lead_id, lead_type, lead_price)
```

Defining the product action and adding products to the event:

Definition:
```
def set_product_action(self, action)

def new_product(self, id=None, name=None, category=None, brand=None,
                price=None, quantity=None)
```

Examples:

```
def some_view_hook(self):

    event = self.request.trackers.ga.new_event(
        'verified lead', 'Frontpoint', 'click')

    event.new_transaction(lead_id, lead_type, lead_price)
    event.set_product_action('purchase')

    product = event.new_product(
        brand_id, campaign_name, campaign_category, campaign_name,
        lead_price, 1)
```

Adding custom dimensions and metrics to a product:
> Every product value needs to be prefixed with its index in the enchanted
> ecommerce array, the API already does it for you, so just add the dimension
> or metric constant name.

**IMPORTANT:** Product custom dimensions and custom metrics should only have
a product scope, so only use constants with `_PS_` as prefix.

Examples:

```
def some_view_hook(self):

    event = self.request.trackers.ga.new_event(
        'verified lead', 'Frontpoint', 'click')

    event.new_transaction(lead_id, lead_type, lead_price)
    event.set_product_action('purchase')

    product = event.new_product(
        brand_id, campaign_name, campaign_category, campaign_name,
        lead_price, 1)

    product[metrics.CM19_PS_VERIFIED_CALL_LEAD] = 0
    product[metrics.CM20_PS_VERIFIED_CLICK_LEAD] = 1
    product[metrics.CM21_PS_VERIFIED_FORM_LEAD] = 0
    product[metrics.CM23_PS_VERIFIED_LEAD] = 1
```

And that's it! Just let the middleware take care of the rest for you :-)

## Implementing a new tracker

When implementing a new tracker, please create a new directory for it, as you
see that we have `ga`, inherit the new tracker class from the abstract `Tracker`
existent in `catracking.core` and update this README with the docs for it.
