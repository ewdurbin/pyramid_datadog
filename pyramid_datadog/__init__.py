from pyramid.events import ApplicationCreated, NewResponse, NewRequest


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


def on_new_request(new_request_event):
    print 'Pyramid triggered a NewRequest event'
    datadog = new_request_event.request.registry.datadog
    datadog.increment('pyramid.request.count', tags=['pyramid_datadog'])

def on_new_response(new_response_event):
    print 'Pyramid triggered a NewResponse event'


def includeme(config):
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_new_response, NewResponse)
