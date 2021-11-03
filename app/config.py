import os

host = os.environ.get('DATABASE_HOST', 'localhost')
REDIS_URL = f"redis://{host}:6379/1"
