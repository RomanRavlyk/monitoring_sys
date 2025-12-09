from services.server import ServerService
from services.healthcheck import HealthCheckService
from services.alert import AlertService
from services.user import UserService
from schemas.report import (ReportContext, ReliabilityMetrics,
                            ErrorStatistics, ErrorByType,
                            TimelineItem, ServerReportResponse, GeneralReportRequest)
from datetime import datetime, timedelta, timezone
from models.healthcheck import HealthCheck
from models.alert import Alert
from typing import List


class ReportService:
    def __init__(self, db, server_service, healthcheck_service, alert_service):
        self._db = db
        self._server_service = server_service
        self._healthcheck_service = healthcheck_service
        self._alert_service = alert_service

    @property
    def db(self):
        return self._db

    @property
    def server_service(self):
        return self._server_service

    @property
    def healthcheck_service(self):
        return self._healthcheck_service

    @property
    def alert_service(self):
        return self._alert_service

    @staticmethod
    async def get_reliability_metrics(health_checks: List[HealthCheck]) -> ReliabilityMetrics:
        success_count: int = sum(1 for hc in health_checks if hc.success)
        failure_count: int = sum(1 for hc in health_checks if not hc.success)

        total = success_count + failure_count
        uptime_percentage: float = (success_count / total * 100) if total > 0 else 0
        total_downtime: timedelta = timedelta()

        sorted_checks = sorted(health_checks, key=lambda hc: hc.checked_at)

        i = 0
        while i < len(sorted_checks):
            if not sorted_checks[i].success:
                downtime_start = sorted_checks[i].checked_at

                j = i + 1
                while j < len(sorted_checks) and not sorted_checks[j].success:
                    j += 1

                if j < len(sorted_checks):
                    downtime_end = sorted_checks[j].checked_at
                    total_downtime += (downtime_end - downtime_start)
                    i = j
                else:
                    total_downtime += (datetime.now(timezone.utc) - downtime_start)
                    break
            else:
                i += 1

        return ReliabilityMetrics(
            uptime_percentage=uptime_percentage,
            total_downtime_minutes=int(total_downtime.total_seconds() // 60),
            healthcheck_success_count=success_count,
            healthcheck_fail_count=failure_count
        )

    @staticmethod
    async def get_error_statistics(alerts: List[Alert]) -> (
            ErrorStatistics,
            List[ErrorByType]
    ):
        total_errors_count = sum(1 for a in alerts)
        critical_errors_count = sum(1 for alert in alerts if alert.severity == "Critical")
        errors_stats_objects: List[ErrorByType] = []
        error_stats = {}

        for alert in alerts:
            if alert.error_type not in error_stats:
                error_stats[alert.error_type] = 0
            error_stats[alert.error_type] += 1

        for error_type, count in error_stats.items():
            errors_stats_objects.append(
                ErrorByType(
                    type=error_type,
                    count=count
                )
            )

        return (ErrorStatistics(total_errors_count=total_errors_count,
                                critical_errors_count=critical_errors_count
                                ),
                errors_stats_objects
                )

    @staticmethod
    async def get_timeline_data(alerts):
        timeline_items: List[TimelineItem] = []
        timelines = {}

        for alert in alerts:
            alert_date = alert.alert_created.date()
            if alert_date not in timelines:
                timelines[alert_date] = 0
            timelines[alert_date] += 1

        for alert_date, count in timelines.items():
            timeline_items.append(
                TimelineItem(
                    date=alert_date,
                    error_count=count
                )
            )
        return timeline_items

    async def generate_report(self, data: GeneralReportRequest):
        server = await self.server_service.get_server_by_id(data.server_id)

        report_context = ReportContext(
            server_id=server.id,
            server_name=server.name,
            period_start = data.period_start,
            period_end = data.period_end
        )

        health_checks_all = await self.healthcheck_service.get_health_checks(data.server_id)
        health_checks = [hc for hc in health_checks_all
                         if data.period_start <= hc.checked_at <= data.period_end
                         ]
        reliability_metrics = await self.get_reliability_metrics(
            health_checks
        )

        alerts = await self.alert_service.get_alerts_by_server(data.server_id)

        error_statistics, errors_by_type = await self.get_error_statistics(alerts)

        timelines_data: List[TimelineItem] = await self.get_timeline_data(alerts)


        return ServerReportResponse(
            report_context=report_context,
            reliability_metrics=reliability_metrics,
            error_statistics=error_statistics,
            errors_by_type=errors_by_type,
            timeline_data=timelines_data
        )
