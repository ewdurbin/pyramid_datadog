import mock


def test_includeme():
    from pyramid_datadog import includeme

    config = mock.Mock()

    configure_metrics = mock.Mock()
    on_app_created = mock.Mock()
    on_new_request = mock.Mock()
    on_before_traversal = mock.Mock()
    on_context_found = mock.Mock()
    on_before_render = mock.Mock()
    on_app_created = mock.Mock()

    ApplicationCreated = mock.Mock()
    NewRequest = mock.Mock()
    BeforeTraversal = mock.Mock()
    ContextFound = mock.Mock()
    BeforeRender = mock.Mock()
    ApplicationCreated = mock.Mock()

    includeme(config)

    assert config.add_directive.called_once_with('configure_metrics', configure_metrics)
    assert config.add_subscriber.called_once_with(on_app_created, ApplicationCreated)
    assert config.add_subscriber.called_once_with(on_new_request, NewRequest)
    assert config.add_subscriber.called_once_with(on_before_traversal, BeforeTraversal)
    assert config.add_subscriber.called_once_with(on_context_found, ContextFound)
    assert config.add_subscriber.called_once_with(on_before_render, BeforeRender)
    assert config.add_subscriber.called_once_with(on_app_created, ApplicationCreated)
