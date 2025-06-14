def generate_telegraf_config(token: str, server_ip: str) -> str:
    return f"""[global_tags]
  token = "{token}"

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

[[processors.converter]]
  [processors.converter.fields]
    float = [
      "load1", 
      "load5", 
      "load15", 
      "inodes_used_percent", 
      "io_util", 
      "usage_steal", 
      "usage_guest_nice",
      "n_cpus"
    ]

[[outputs.influxdb_v2]]
  urls = ["https://us-east-1-1.aws.cloud2.influxdata.com"]
  token = "zpBn3XHjYBTSI4ssitgbV6Lujsi18qtY6ydiFhbvfZfdZ5_iQG6hmmHVJTHgQ-IJ5oD0BDgrnTJ-aHAOZdvzlg=="
  organization = "dev team"
  bucket = "server_metrics"
"""