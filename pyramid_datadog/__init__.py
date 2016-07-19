import time


from pyramid.events import ApplicationCreated, NewResponse, NewRequest, ContextFound, BeforeTraversal, BeforeRender


def configure_metrics(config, datadog_metrics):
    print 'configure_metrics called'
    config.registry.datadog = datadog_metrics


def on_app_created(app_created_event):
    datadog = app_created_event.app.registry.datadog
    datadog.event(
        "Pyramid app started",
        "The Pyramid application has started",
        tags=["pyramid_datadog:app_started"]
    )


def on_new_request(new_request_event):
    print 'Pyramid triggered a NewRequest event'
    datadog = new_request_event.request.registry.datadog
    req = new_request_event.request
    req.start_time = time.time()
    datadog.increment(
        'pyramid.request.count',
        tags=['pyramid_datadog:request_count']
    )


def on_new_response(new_response_event):
    print 'Pyramid triggered a NewResponse event'
    datadog = new_response_event.request.registry.datadog
    request = new_response_event.request
    duration = time.time() - request.start_time
    template_render_time = time.time() - request.before_render_start
    datadog.timing(
        'pyramid.request.time', duration,
        tags=['pyramid_datadog:request_time'],
    )
    datadog.timing(
        'pyramid.template.time', duration,
        tags=['pyramid_datadog:template_time'],
    )


def on_context_found(context_found_event):
    print 'ContextFound' 
    datadog = context_found_event.request.registry.datadog
    start_time = context_found_event.request.start_time
    duration = time.time() - start_time
    request = context_found_event.request
    request.view_start = time.time()
    datadog.timing(
        'pyramid.context_found.time', duration,
        tags=['pyramid_datadog:context_found'],
    )


def on_before_traversal(before_traversal_event):
    print 'BeforeTraversal'
    datadog = before_traversal_event.request.registry.datadog
    start_time = before_traversal_event.request.start_time
    duration = time.time() - start_time
    datadog.timing(
        'pyramid.traversal.time', duration,
        tags=['pyramid_datadog:traversal'],
    )


def on_before_render(before_render_event):
    print 'BeforeRender'
    datadog = before_render_event['request'].registry.datadog
    view_start = before_render_event['request'].view_start
    view_duration = time.time() - view_start
    datadog.timing(
        'pyramid.view_duration', view_duration,
        tags=['pyramid_datadog'],
    )
    request.before_render_start = time.time()

def includeme(config):
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_new_response, NewResponse)
    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_traversal, BeforeTraversal)
    config.add_subscriber(on_before_render, BeforeRender)
