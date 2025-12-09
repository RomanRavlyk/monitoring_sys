from fastapi import APIRouter, Query, Depends
from schemas.report import ServerReportResponse, GeneralReportRequest
from deps import get_report_service
from datetime import datetime
from services.report import ReportService

router = APIRouter(tags=["Report"])

@router.get("/reports/{server_id}", response_model=ServerReportResponse)
async def get_system_report(server_id: int,
                            start_date: datetime = Query(),
                            end_date: datetime = Query(),
                            service: ReportService = Depends(get_report_service)
                            ):

    data = {
        "server_id": server_id,
        "period_start": start_date,
        "period_end": end_date
    }

    validated_data = GeneralReportRequest.model_validate(data)

    return await service.generate_report(validated_data)




