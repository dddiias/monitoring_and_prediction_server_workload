def generate_telegraf_config(token: str, server_ip: str) -> str:
    return f"""
[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"

[[inputs.cpu]]
  percpu = false
  totalcpu = true
  fielddrop = ["time_*"]

[[inputs.mem]]

[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs"]

[[inputs.diskio]]

[[inputs.net]]

[[inputs.system]]

[[inputs.processes]]

[[inputs.kernel]]

[[outputs.http]]
  url = "http://{server_ip}:8000/telegraf"
  method = "POST"
  data_format = "json"

  [outputs.http.headers]
    token = "{token}"
"""