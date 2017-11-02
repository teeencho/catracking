# catracking

This package is responsible for all the tracking considered "cross-application" in our codebase.
Currently, the only tracker implemented is for Google Analytics (Measurement Protocol)

## Usage

### Configuration

Each tracker will have its own configuration dictionary, inside `TRACKERS`.
If the tracker is not configured and the middleware is being used, exceptions will be thrown.
The configuration parameters should vary according to which environment you are.

#### GA

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
      'DOCUMENT_HOSTNAME': 'consumeraffairs.com'
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
