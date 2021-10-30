import pytest
from flask import url_for


def test_get_all_domains(app, client):

    app.redis.lpush('1', 'https://www.example.com')
    app.redis.lpush('10', 'https://www.example.com', 'https://www.thirdexample.com')
    app.redis.lpush('100', 'https://www.anotherexample.com', 'https://www.test.com', 'https://www.python.com')

    response = client.get('/visited_domains')
    response_json = response.get_json()
    assert response.status_code == 200
    assert len(response_json['domains']) == 5


@pytest.mark.parametrize(
    ['start', 'stop', 'instance_count', 'status_code'],
    (
        ("9", "10",  2, 200),
        ("10", "11",  2, 200),
        ("11", "10",  2, 200),
        ("10", "9",  2, 200),
        ("10", "10",  1, 200),
        ("9", "11",  3, 200),
        ("11", "9",  3, 200),
    )
)
def test_closest_intervals(app, client, start, stop, instance_count, status_code):

    app.redis.lpush('9', 'https://www.example.com')
    app.redis.lpush('10', 'https://www.anotherexample.com')
    app.redis.lpush('11', 'https://www.thirdexample.com')

    q_params = {
        'from': start,
        'to': stop
    }

    response = client.get('/visited_domains', query_string=q_params)
    response_json = response.get_json()
    assert response.status_code == status_code
    assert len(response_json['domains']) == instance_count


@pytest.mark.parametrize(
    ['stop', 'instance_count', 'status_code'],
    (
        ("9",  0, 200),
        ("10",  1, 200),
        ("101",  2, 200),
        ("160",  3, 200),
    )
)
def test_interval_without_start(app, client, stop, instance_count, status_code):

    app.redis.lpush('10', 'https://www.example.com')
    app.redis.lpush('100', 'https://www.anotherexample.com')
    app.redis.lpush('150', 'https://www.thirdexample.com')

    q_params = {
        'to': stop
    }

    response = client.get('/visited_domains', query_string=q_params)
    response_json = response.get_json()
    assert response.status_code == status_code
    assert len(response_json['domains']) == instance_count


@pytest.mark.parametrize(
    ['start', 'instance_count', 'status_code'],
    (
        ("9",  3, 200),
        ("11",  2, 200),
        ("101",  1, 200),
        ("160",  0, 200),
    )
)
def test_interval_without_stop(app, client, start, instance_count, status_code):

    app.redis.lpush('10', 'https://www.example.com')
    app.redis.lpush('100', 'https://www.anotherexample.com')
    app.redis.lpush('150', 'https://www.thirdexample.com')

    q_params = {
        'from': start
    }

    response = client.get('/visited_domains', query_string=q_params)
    response_json = response.get_json()
    assert response.status_code == status_code
    assert len(response_json['domains']) == instance_count


@pytest.mark.parametrize(
    ['start', 'stop', 'instance_count', 'status_code'],
    (
        ("0", "9",  0, 200),
        ("0", "20",  1, 200),
        ("20", "70",  1, 200),
        ("20", "110",  2, 200),
        ("110", "200",  0, 200),
    )
)
def test_outer_data(app, client, start, stop, instance_count, status_code):
    app.redis.lpush('10', 'https://www.example.com')
    app.redis.lpush('50', 'https://www.anotherexample.com')
    app.redis.lpush('100', 'https://www.thirdexample.com')

    q_params = {
        'from': start,
        'to': stop
    }

    response = client.get('/visited_domains', query_string=q_params)
    response_json = response.get_json()
    assert response.status_code == status_code
    assert len(response_json['domains']) == instance_count


def test_bad_args(app, client):
    app.redis.lpush('10', 'https://www.example.com')
    app.redis.lpush('50', 'https://www.anotherexample.com')

    q_params = {
        'from': 'not int',
        'to': '@@'
    }

    response = client.get('/visited_domains', query_string=q_params)
    response_json = response.get_json()
    assert response.status_code == 400
    assert response_json.get('domains') is None


def test_unique_domains(app, client):
    app.redis.lpush('10', 'https://www.example.com')
    app.redis.lpush('50', 'https://www.anotherexample.com', 'https://www.example.com')

    response = client.get('/visited_domains')
    response_json = response.get_json()
    assert response.status_code == 200
    assert len(response_json['domains']) == 2


@pytest.mark.parametrize(
    ['url', 'status_code', 'data_through'],
    (
        ('https://www.example.com', 201, 1),
        ('http://www.example.com', 201, 1),
        ('www.example.com', 201, 1),
        ('example.com', 201, 1),
        ('http://blog.example.com', 201, 1),
        ('http://www.example.com/product', 201, 1),
        ('http://www.example.com/products?id=1&page=2', 201, 1),
        ('invalid_url', 400, 0)
    )
)
def test_regex(app, client, url, status_code, data_through):

    data = {
        'links': [
            url
        ]
    }

    response = client.post('/visited_links/', json=data)
    assert len(app.redis.keys(pattern='*')) == data_through
    assert response.status_code == status_code


@pytest.mark.parametrize(
    ['test_json', 'status_code', 'data_through'],
    (
        ({'links': ['http://www.example.com']}, 201, 1),
        ({'links': ['http://www.example.com'], 'extra_key': 'extra_value'}, 400, 0),
        ({'linkss': ['http://www.example.com']}, 400, 0),
        ({'links': 2}, 400, 0),
        ({'linkss': 'invalid_string'}, 400, 0),
    )
)
def test_json_schema(app, client, test_json, status_code, data_through):
    data = test_json
    response = client.post('/visited_links/', json=data)
    assert len(app.redis.keys(pattern='*')) == data_through
    assert response.status_code == status_code
