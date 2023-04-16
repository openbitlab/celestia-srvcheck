from prometheus_client import Gauge, start_http_server, Counter, Info, Enum
from typing import Any


class Exporter:
    metrics = None

    def __init__(self, metrics: dict[object, callable[..., Any]], port: int):
        start_http_server(port)
        self.metrics = metrics

    def export(self):
        for m, v in self.metrics.items():
            m.set(v())
