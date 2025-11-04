broker_url = "redis://83.166.245.209:6379/0"
result_backend = "redis://83.166.245.209:6379/0"
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Krasnoyarsk"
enable_utc = True

worker_concurrency = 1
worker_prefetch_multiplier = 1
