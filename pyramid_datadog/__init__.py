from pyramid.events import ApplicationCreated


def configure_metrics(config, datadog_metrics):
    print 'configure_metrics called'
    config.registry.datadog = datadog_metrics


def on_app_created(app_created_event):
    datadog = app_created_event.app.registry.datadog
    datadog.event(
        "Pyramid app started",
        "The Pyramid application has started",
        tags=["pyramid_datadog"]
    )


def includeme(config):
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
