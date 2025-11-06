from redis.sentinel import Sentinel

from project.settings import POSTGRES_HOST

s = Sentinel(
    [(f"{POSTGRES_HOST}", 26379), (f"{POSTGRES_HOST}", 26379)], socket_timeout=0.5
)
try:
    # Попробуйте найти мастер с разными именами
    master_host, master_port = s.discover_master("mymaster")
except:
    try:
        master_host, master_port = s.discover_master("redis-master")
    except:
        try:
            master_host, master_port = s.discover_master("wink_redis")
        except:
            # Если Sentinel не настроен, используем мастера напрямую
            master_host = POSTGRES_HOST
            master_port = 6379

broker_url = f"redis://{master_host}:{master_port}/0"
result_backend = f"redis://{master_host}:{master_port}/0"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Krasnoyarsk"
enable_utc = True

worker_concurrency = 1
worker_prefetch_multiplier = 1
task_track_started = True
task_time_limit = 60 * 60 * 12
