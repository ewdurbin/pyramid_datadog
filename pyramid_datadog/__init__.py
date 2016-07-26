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


def configure_metrics(config, app_name, datadog_metrics):
    '''
    * app_name: name of your application that will be in a tag
    * datadog_metrics: datadog metrics object initialized by user
    '''
    config.registry.datadog = datadog_metrics
    config.registry.datadog_app_name = app_name
    config.registry.datadog_app_tag = "app:%s" % app_name


def on_app_created(app_created_event):
    registry = app_created_event.app.registry
    datadog = registry.datadog
    datadog.event(
        'Pyramid application %s started' % registry.datadog_app_name,
        'Pyramid application %s started' % registry.datadog_app_name,
        tags=[registry.datadog_app_tag]
    )


def on_new_request(new_request_event):
    request = new_request_event.request
    request.timings = {}
    request.timings['new_request_start'] = time_ms()

    datadog = request.registry.datadog
    datadog.increment(
        'pyramid.request.count',
        tags=[request.registry.datadog_app_tag],
    )


def on_before_traversal(before_traversal_event):
    request = before_traversal_event.request

    timings = request.timings
    timings['route_match_duration'] = time_ms() - timings['new_request_start']

    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.route_match.duration',
        timings['route_match_duration'],
        tags=[request.registry.datadog_app_tag],
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
        tags=[request.registry.datadog_app_tag],
    )


def on_before_render(before_render_event):
    request = before_render_event['request']

    timings = request.timings
    timings['view_duration'] = time_ms() - timings['view_code_start']
    timings['before_render_start'] = time_ms()

    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.view.duration',
        timings['view_duration'],
        tags=[request.registry.datadog_app_tag],
    )


def on_new_response(new_response_event):
    request = new_response_event.request
    new_response_time = time_ms()

    timings = request.timings
    timings['request_duration'] = \
        new_response_time - timings['new_request_start']
    timings['template_render_duration'] = \
        new_response_time - timings['before_render_start']

    datadog = request.registry.datadog
    route_tag = "route:%s" % request.matched_route.name
    datadog.timing(
        'pyramid.request.duration',
        timings['request_duration'],
        tags=[request.registry.datadog_app_tag, route_tag],
    )
    datadog.timing(
        'pyramid.template_render.duration',
        timings['template_render_duration'],
        tags=[request.registry.datadog_app_tag, route_tag],
    )

    status_code = request.response.status
    datadog.increment(
        'pyramid.response.status_code.%s' % status_code,
        tags=[request.registry.datadog_app_tag, route_tag],
    )

    datadog.increment(
        'pyramid.response.status_code.%sxx' % status_code[0],
        tags=[request.registry.datadog_app_tag, route_tag],
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
