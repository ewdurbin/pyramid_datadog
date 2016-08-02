import mock
from mock import patch
from pyramid_datadog import (
    includeme,
    configure_metrics,
    on_app_created,
    on_new_request,
    on_before_traversal,
    on_context_found,
    on_before_render,
    on_new_response,
    time_ms,
)


def test_includeme():
    from pyramid.events import (
        ApplicationCreated,
        NewResponse,
        NewRequest,
        ContextFound,
        BeforeTraversal,
        BeforeRender)

    config = mock.Mock()

    includeme(config)
    config.add_directive.assert_called_once_with('configure_metrics', configure_metrics)
    config.add_subscriber.assert_has_calls([
        mock.call(on_app_created, ApplicationCreated),
        mock.call(on_new_request, NewRequest),
        mock.call(on_before_traversal, BeforeTraversal),
        mock.call(on_context_found, ContextFound),
        mock.call(on_before_render, BeforeRender),
        mock.call(on_new_response, NewResponse),
    ])


def test_configure_metrics():
    config = mock.Mock()
    datadog_metrics = mock.Mock()
    configure_metrics(config, 'app_name', datadog_metrics)

    config.registry.datadog == datadog_metrics
    config.registry.datadog_app_name = 'app_name'
    config.registry.datadog_app_tag = 'app:app_name'


def test_on_app_created():
    app_created_event = mock.Mock()
    app_created_event.app.registry.datadog = mock.Mock()
    app_created_event.app.registry.datadog_app_name = 'app_name'
    app_created_event.app.registry.datadog_app_tag = 'app:app_name'
    on_app_created(app_created_event)

    app_created_event.app.registry.datadog.event.assert_called_once_with(
        'Pyramid application app_name started',
        'Pyramid application app_name started',
        tags=['app:app_name']
    )


@patch('pyramid_datadog.time_ms')
def test_on_new_request(time_ms_mock):
    new_request_event = mock.Mock()
    time_ms_mock.return_value = 1
    on_new_request(new_request_event)

    assert new_request_event.request.timings['new_request_start'] == 1


@patch('pyramid_datadog.time_ms')
def test_on_before_traversal(time_ms_mock):
    before_traversal_event = mock.Mock()
    before_traversal_event.request.timings = {}
    before_traversal_event.request.timings['new_request_start'] = 1
    before_traversal_event.request.registry.datadog_app_tag = 'app:app_name'
    time_ms_mock.return_value = 2

    on_before_traversal(before_traversal_event)
    before_traversal_event.request.registry.datadog.timing.assert_called_once_with(
        'pyramid.request.duration.route_match',
        1,
        tags=['app:app_name']
    )


@patch('pyramid_datadog.time_ms')
def test_on_context_found(time_ms_mock):
    context_found_event = mock.Mock()
    context_found_event.request.timings = {}
    context_found_event.request.timings['new_request_start'] = 1
    context_found_event.request.registry.datadog_app_tag = 'app:app_name'
    time_ms_mock.return_value = 3

    on_context_found(context_found_event)
    assert context_found_event.request.timings['view_code_start'] == 3
    context_found_event.request.registry.datadog.timing.assert_called_once_with(
        'pyramid.request.duration.traversal',
        2,
        tags=['app:app_name']
    )


@patch('pyramid_datadog.time_ms')
def test_on_before_render(time_ms_mock):
    before_render_event = mock.Mock()
    before_render_event = {'request': mock.Mock()}
    timings = before_render_event['request'].timings = {}
    before_render_event['request'].registry.datadog_app_tag = 'app:app_name'
    timings['view_code_start'] = 3
    time_ms_mock.return_value = 4

    on_before_render(before_render_event)

    assert timings['view_duration'] == 1
    assert timings['before_render_start'] == 4

    before_render_event['request'].registry.datadog.timing.assert_called_once_with(
        'pyramid.request.duration.view',
        1,
        tags=['app:app_name']
    )


@patch('pyramid_datadog.time_ms')
def test_on_new_response(time_ms_mock):
    new_response_event = mock.Mock()
    new_response_event.request.registry.datadog_app_tag = 'app:app_name'
    new_response_event.request.matched_route.name = 'test_route'
    new_response_event.response.status_code = 200
    time_ms_mock.return_value = 5
    timings = new_response_event.request.timings = {}
    timings['new_request_start'] = 1
    timings['before_render_start'] = 4

    on_new_response(new_response_event)

    assert timings['request_duration'] == 4
    assert timings['template_render_duration'] == 1
    new_response_event.request.registry.datadog.timing.assert_has_calls([
        mock.call(
            'pyramid.request.duration.template_render',
            1,
            tags=['app:app_name', 'route:test_route']
        ),
        mock.call(
            'pyramid.request.duration.total',
            4,
            tags=['app:app_name', 'route:test_route', 'status_code:200', 'status_type:2xx']
        ),
    ])


@patch('time.time')
def test_time_ms(mock_time):
    mock_time.return_value = 1
    return_value = time_ms()
    assert return_value == 1000
