def generate_telegraf_config(token: str, server_ip: str) -> str:
    return f"""
[agent]
  interval = "10s"

[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false

[[inputs.mem]]

[[outputs.http]]
  url = "http://{server_ip}:8000/telegraf"
  method = "POST"
  data_format = "json"

  [outputs.http.headers]
    token = "{token}"
"""
