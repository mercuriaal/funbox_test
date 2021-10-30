from fakeredis import FakeServer, FakeStrictRedis
from flask_redis import FlaskRedis


def config_redis(testing):
    if not testing:
        redis_client = FlaskRedis()
    else:
        server = FakeServer()
        fake_redis = FakeStrictRedis(server=server)
        redis_client = FlaskRedis.from_custom_provider(fake_redis)
    return redis_client
