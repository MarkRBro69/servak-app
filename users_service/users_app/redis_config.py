import os

import redis

local_host = '127.0.0.4'

if os.getenv('RUNNING_IN_DOCKER'):
    redis_host = 'redis'
else:
    redis_host = local_host

r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

