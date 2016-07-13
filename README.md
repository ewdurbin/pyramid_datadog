# pyramid_datadog

Datadog integration for Pyramid.

## Installation

```python
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
