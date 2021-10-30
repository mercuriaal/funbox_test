import time
from urllib.parse import urlparse

from flask import request, jsonify, Blueprint, current_app, make_response
import jsonschema

from app import schema

links = Blueprint('links', __name__, url_prefix='')


@links.route('/visited_domains', methods=('GET',))
def get_domains():

    try:
        start = int(request.args.get('from', 0))
        stop = int(request.args.get('to', int(time.time_ns()))) + 1
    except ValueError:
        response = make_response(jsonify({'status': 'requested interval is not an integer'}))
        response.status_code = 400
        return response

    set_of_domains = set()
    step = 1

    if start >= stop:
        step = -1
        stop -= 2

    for key in current_app.redis.scan_iter():
        if int(key) in range(start, stop, step):
            domains = set(current_app.redis.lrange(key, 0, -1))
            set_of_domains = set_of_domains.union(domains)

    domain_array = [domain.decode('utf-8') for domain in list(set_of_domains)]
    data = {'domains': domain_array, 'status': 'ok'}

    return jsonify(data)


@links.route('/visited_links/', methods=('POST',))
def post_links():

    try:
        jsonschema.validate(request.json, schema=schema.LINKS_SCHEMA)
    except jsonschema.ValidationError as err:
        response = make_response(jsonify({'status': err.message}))
        response.status_code = 400
        return response

    data = request.json['links']
    key = int(time.time())
    for string in data:
        if not string.startswith('https://'):
            link = '//' + string
        else:
            link = string
        parse = urlparse(link)
        name = parse.netloc
        current_app.redis.lpush(key, name)

    return jsonify({'status': 'ok'}), 201
