# pyramid_datadog

Datadog integration for Pyramid.
This library allows you to create graphs in datadog to keep track of number of requests and requests durations.

## Installation

```
pip install pyramid_datadog
```

## Usage

```python
from datadog import statsd


def main(global_config, **settings):

    # pyramid initialization

    config.include("pyramid_datadog")
    config.configure_metrics(statsd)

    return config.make_wsgi_app()
```

## What pyramid_datadog will measure for you

```
Using pyramid.events pyramid_datadog will log the following metrics in datadog:
```

```python
  pyramid.request.duration.route_match
  pyramid.request.duration.traversal
  pyramid.request.duration.view
  pyramid.request.duration.template_render tags = route
  pyramid.request.duration.total tags = route, status_code and status_type
```

```
Please refer to http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/router.html
```
