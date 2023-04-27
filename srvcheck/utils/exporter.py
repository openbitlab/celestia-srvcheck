from prometheus_client import Gauge, start_http_server, Counter, Info, Enum
from typing import Any


class Exporter:
    metrics = None

    def __init__(self, metrics: dict, port):
        start_http_server(port)
        self.metrics = metrics

    def export(self):
        for m, v in self.metrics.items():
            if type(m) is Gauge:
                m.set(v())
            elif type(m) is Counter:
                m.inc(int(v()))
