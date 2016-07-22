import time


from pyramid.events import (
    ApplicationCreated,
    NewResponse,
    NewRequest,
    ContextFound,
    BeforeTraversal,
    BeforeRender)


def time_ms():
    return time.time() * 1000


def configure_metrics(config, datadog_metrics):
    config.registry.datadog = datadog_metrics


def on_app_created(app_created_event):
    datadog = app_created_event.app.registry.datadog
    datadog.event(
        'Pyramid_app_started',
        'The Pyramid application has started',
        tags=['pyramid_datadog']
    )


def on_new_request(new_request_event):
    request = new_request_event.request
    request.timings = {}
    request.timings['new_request_start'] = time_ms()
    datadog = request.registry.datadog
    datadog.increment(
        'pyramid.request.count',
        tags=['pyramid_datadog'],
    )


def on_before_traversal(before_traversal_event):
    request = before_traversal_event.request
    timings = request.timings
    datadog = request.registry.datadog
    timings['route_match_duration'] = time_ms() - timings['new_request_start']
    datadog.timing(
        'pyramid.route_match.duration',
        timings['route_match_duration'],
        tags=['pyramid_datadog'],
    )


def on_context_found(context_found_event):
    request = context_found_event.request
    timings = request.timings
    timings['traversal_duration'] = time_ms() - timings['new_request_start']
    timings['view_code_start'] = time_ms()
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.traversal.duration',
        timings['traversal_duration'],
        tags=['pyramid_datadog'],
    )


def on_before_render(before_render_event):
    request = before_render_event['request']
    timings = request.timings
    timings['view_duration'] = time_ms() - timings['view_code_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.view_duration',
        timings['view_duration'],
        tags=['pyramid_datadog'],
    )
    timings['before_render_start'] = time_ms()


def on_new_response(new_response_event):
    request = new_response_event.request
    timings = request.timings
    new_response_time = time_ms()
    timings['request_duration'] = \
        new_response_time - timings['new_request_start']
    timings['template_render_duration'] = \
        new_response_time - timings['before_render_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.request.duration',
        timings['request_duration'],
        tags=['pyramid_datadog'],
    )
    datadog.timing(
        'pyramid.template_render.duration',
        timings['template_render_duration'],
        tags=['pyramid_datadog'],
    )

    status_code = request.response.status
    datadog.increment(
        'pyramid.response.http.status_code.%s' % status_code,
        tags=['pyramid_datadog'],
    )

    datadog.increment(
        'pyramid.response.http.status_code.%sxx' % status_code[0],
        tags=['pyramid_datadog'],
    )


def includeme(config):
    '''
    Events are triggered in the following chronological order:
    NewRequest > BeforeTraversal > ContextFound > BeforeRender > NewResponse
    '''
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_before_traversal, BeforeTraversal)
    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_response, NewResponse)
