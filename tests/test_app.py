import pytest
from page_analyzer.app import app


@pytest.fixture()
def app():
    application = app
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_example(client):
    response = client.get("/")
    assert "Page Analyzer" in response.data
