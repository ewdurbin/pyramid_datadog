import time


from pyramid.events import (
    ApplicationCreated,
    NewResponse,
    NewRequest,
    ContextFound,
    BeforeTraversal,
    BeforeRender)


def configure_metrics(config, datadog_metrics):
    config.registry.datadog = datadog_metrics


def on_app_created(app_created_event):
    datadog = app_created_event.app.registry.datadog
    datadog.event(
        'Pyramid app started',
        'The Pyramid application has started',
        tags=['pyramid_datadog']
    )


def on_new_request(new_request_event):
    request = new_request_event.request
    request.timings = {}
    request.timings['new_request_start'] = time.time()
    datadog = request.registry.datadog
    datadog.increment(
        'pyramid.request.count',
        tags=['pyramid_datadog'],
    )


def on_before_traversal(before_traversal_event):
    pass


def on_context_found(context_found_event):
    request = context_found_event.request
    timings = request.timings
    timings['route_match_duration'] = \
        time.time() - timings['new_request_start']
    timings['view_code_start'] = time.time()
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.route_match.duration',
        timings['route_match_duration'],
        tags=['pyramid_datadog'],
    )


def on_before_render(before_render_event):
    request = before_render_event['request']
    timings = request.timings
    timings['view_duration'] = time.time() - timings['view_code_start']
    datadog = request.registry.datadog
    datadog.timing(
        'pyramid.view_duration',
        timings['view_duration'],
        tags=['pyramid_datadog'],
    )
    timings['before_render_start'] = time.time()


def data_dog_increment_status_code(status_code, datadog):

    granular_status_code_query_string = 'pyramid.request.http.status_code.%s'\
        % status_code
    datadog.increment(
        granular_status_code_query_string,
        tags=['pyramid_datadog'],
    )

    status_code_query_string = 'pyramid.request.http.status_code.%sxx'\
        % status_code[0]
    datadog.increment(
        status_code_query_string,
        tags=['pyramid_datadog'],
    )


def on_new_response(new_response_event):
    request = new_response_event.request
    timings = request.timings
    new_response_time = time.time()
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
    data_dog_increment_status_code(status_code, datadog)


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
