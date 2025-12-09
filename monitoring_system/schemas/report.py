from pydantic import BaseModel
from datetime import datetime, date
from typing import List

class GeneralReportRequest(BaseModel):
    server_id: int
    period_start: datetime
    period_end: datetime

class ReportContext(BaseModel):
    server_id: int
    server_name: str
    period_start: datetime
    period_end: datetime


class ReliabilityMetrics(BaseModel):
    uptime_percentage: float
    total_downtime_minutes: int
    healthcheck_success_count: int
    healthcheck_fail_count: int


class ErrorStatistics(BaseModel):
    total_errors_count: int
    critical_errors_count: int


class ErrorByType(BaseModel):
    type: str
    count: int


class TimelineItem(BaseModel):
    date: date
    error_count: int


class ServerReportResponse(BaseModel):
    report_context: ReportContext
    reliability_metrics: ReliabilityMetrics
    error_statistics: ErrorStatistics
    errors_by_type: List[ErrorByType]
    timeline_data: List[TimelineItem]