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

Using pyramid.events pyramid_datadog will log the following metrics in datadog:


| Metric                                  | Tags                           |
| ----------------------------------------|--------------------------------|
| pyramid.request.duration.route_match    |                                |
| pyramid.request.duration.traversal      |                                |
| pyramid.request.duration.view           | route                          |
| pyramid.request.duration.template_render| route                          |
| pyramid.request.duration.total          | route, status_code, status_type|



Please refer to the following link for information on the chronological order of events during a pyramid request http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/router.html
