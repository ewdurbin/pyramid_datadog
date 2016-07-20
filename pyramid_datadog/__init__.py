import time


from pyramid.events import (
    ApplicationCreated,
    NewResponse,
    NewRequest,
    ContextFound,
    BeforeTraversal,
    BeforeRender)

timings = {}


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
    request = new_request_event.request
    request.timings['new_request_start'] = time.time()
    datadog = request.registry.datadog
    datadog.increment(
        'pyramid.request.count',
        tags=['pyramid_datadog:request_count'],
    )


def on_before_traversal(before_traversal_event):
    print 'BeforeTraversal'
    request = before_traversal_event.request
    request.timings['traversal_duration'] = \
        time.time() - request.timings['new_request_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.traversal.duration',
        request['traversal_duration'],
        tags=['pyramid_datadog:traversal'],
    )


def on_context_found(context_found_event):
    print 'ContextFound'
    request = context_found_event.request
    request.timings['context_found_duration'] = \
        time.time() - request.timings['new_request_start']
    request.timings['view_code_start'] = time.time()
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.context_found.duration',
        request.timings['context_found_duration'],
        tags=['pyramid_datadog:context_found'],
    )


def on_before_render(before_render_event):
    print 'BeforeRender'
    request = before_render_event['request']
    request.timings['view_duration'] = \
        time.time() - request.timings['view_code_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.view_duration',
        request.timings['view_duration'],
        tags=['pyramid_datadog'],
    )
    request.timings['before_render_start'] = time.time()


def on_new_response(new_response_event):
    print 'Pyramid triggered a NewResponse event'
    request = new_response_event.request
    request.timings['request_duration'] = \
        time.time() - request.timings['new_request_start']
    request.timings['template_render_duration'] = \
        time.time() - request.timings['before_render_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.request.duration',
        request.timings['request_duration'],
        tags=['pyramid_datadog:request_time'],
    )
    datadog.timing(
        'pyramid.template_render.duration',
        request.timings['template_render_duration'],
        tags=['pyramid_datadog:template_time'],
    )


def includeme(config):
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_new_response, NewResponse)
    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_traversal, BeforeTraversal)
    config.add_subscriber(on_before_render, BeforeRender)
