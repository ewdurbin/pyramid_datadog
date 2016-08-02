import mock


def test_includeme():

    from pyramid.events import (
        ApplicationCreated,
        NewResponse,
        NewRequest,
        ContextFound,
        BeforeTraversal,
        BeforeRender)

    from pyramid_datadog import (
        includeme,
        configure_metrics,
        on_app_created,
        on_new_request,
        on_before_traversal,
        on_context_found,
        on_before_render,
        on_new_response
    )

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
