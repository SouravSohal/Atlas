import structlog

logger = structlog.get_logger()

class MonitoringClient:
    """Wrapper client for capturing application metrics, traces, and diagnostics."""

    async def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Records a metric for tracking application behavior."""
        logger.info("Metric recorded", metric_name=name, metric_value=value, labels=labels)
