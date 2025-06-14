from logic.influx_metrics import get_latest_metrics


def get_metrics_from_server(token: str, _: str = None) -> dict:
    return get_latest_metrics(token)
