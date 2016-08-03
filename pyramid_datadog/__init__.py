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
    '''
    * datadog_metrics: datadog metrics object initialized by user
    '''
    config.registry.datadog = datadog_metrics


def on_app_created(app_created_event):
    registry = app_created_event.app.registry
    datadog = registry.datadog
    datadog.event(
        'Pyramid application started',
        'Pyramid application started'
    )


def on_new_request(new_request_event):
    request = new_request_event.request
    request.timings = {}
    request.timings['new_request_start'] = time_ms()


def on_before_traversal(before_traversal_event):
    request = before_traversal_event.request

    timings = request.timings
    timings['route_match_duration'] = time_ms() - timings['new_request_start']

    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.request.duration.route_match',
        timings['route_match_duration'],
    )


def on_context_found(context_found_event):
    request = context_found_event.request

    timings = request.timings
    timings['traversal_duration'] = time_ms() - timings['new_request_start']
    timings['view_code_start'] = time_ms()

    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.request.duration.traversal',
        timings['traversal_duration'],
    )


def on_before_render(before_render_event):
    request = before_render_event['request']

    timings = request.timings
    timings['view_duration'] = time_ms() - timings['view_code_start']
    timings['before_render_start'] = time_ms()

    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.request.duration.view',
        timings['view_duration'],
    )


def on_new_response(new_response_event):
    request = new_response_event.request
    new_response_time = time_ms()

    timings = request.timings
    timings['request_duration'] = \
        new_response_time - timings['new_request_start']

    tags = []
    datadog = request.registry.datadog

    if request.matched_route:
        route_tag = 'route:%s' % request.matched_route.name
        tags.append(route_tag)

        if 'before_render_start' in timings:
            timings['template_render_duration'] = \
                new_response_time - timings['before_render_start']

            datadog.timing(
                'pyramid.request.duration.template_render',
                timings['template_render_duration'],
                tags=tags,
            )

    status_code = str(new_response_event.response.status_code)
    datadog.timing(
        'pyramid.request.duration.total',
        timings['request_duration'],
        tags=tags + [
            'status_code:%s' % status_code,
            'status_type:%sxx' % status_code[0]
        ],
    )


def includeme(config):
    '''
    Events are triggered in the following chronological order:
    NewRequest > BeforeTraversal > ContextFound > BeforeRender > NewResponse

    Note that not all events may be triggered depending on the request scenario
    eg. 404 Not Found would not trigger ContextFound event.
    '''
    config.add_directive('configure_metrics', configure_metrics)
    config.add_subscriber(on_app_created, ApplicationCreated)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_before_traversal, BeforeTraversal)
    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_response, NewResponse)
