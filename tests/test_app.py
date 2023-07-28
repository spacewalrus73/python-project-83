import pytest
from page_analyzer.app import app
from page_analyzer.db_actions import select, extract_one, delete


@pytest.fixture()
def reset_app():
    app.testing = True
    yield app
    delete(table_name='urls', where='name', value="https://ru.hexlet.io")


@pytest.fixture()
def client(reset_app):
    return app.test_client()


@pytest.fixture()
def id_test(client):
    client.post("/urls", data={"url": "https://ru.hexlet.io"})
    selected_id = select(table_name="urls",
                         fields=["id"],
                         where="name",
                         param="https://ru.hexlet.io")
    i_d = extract_one(selected_id)
    return i_d


def test_home_page(client):
    response = client.get("/")
    page_data = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Анализатор страниц' in page_data


def test_receive_url(id_test, client):
    response = client.get(f"/urls/{id_test}")
    assert response.status_code == 200
    assert "Страница успешно добавлена" in response.get_data(as_text=True)

    client.post("/urls", data={"url": "https://ru.hexlet.io"})
    response = client.get(f"/urls/{id_test}")
    assert response.status_code == 200
    assert 'Страница уже существует' in response.get_data(as_text=True)

    client.post("/urls", data={"url": ''})
    response = client.get("/")
    assert response.status_code == 200
    assert "URL обязателен" in response.get_data(as_text=True)
    assert "Некорректный URL" in response.get_data(as_text=True)


def test_show_site_page(id_test, client):
    response = client.get(f"/urls/{id_test}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'https://ru.hexlet.io' in html
    assert str(id_test) in html


def test_show_websites(id_test, client):
    response = client.get("/urls")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "ID" in html
    assert "Имя" in html
    assert "Последняя проверка" in html
    assert "Код ответа" in html
    assert str(id_test) in html
    assert 'https://ru.hexlet.io' in html


def test_check(id_test, client):
    client.post(f"/urls/{id_test}/checks")
    response = client.get(f"urls/{id_test}")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Страница успешно проверена" in html
    assert "ID" in html
    assert str(id_test) in html
    assert "Код ответа" in html
    assert "h1" in html
    assert "title" in html
    assert "description" in html
    assert "Дата создания" in html
    delete(table_name='url_checks', where='url_id', value=id_test)
