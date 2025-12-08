from fastapi import APIRouter, Depends
from deps import get_alert_service
from services.alert import AlertService

router = APIRouter(tags=["Alert"])

@router.get("/alerts")
async def get_alerts(alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.get_alerts()

@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: int, alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.get_alert_by_id(alert_id)

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.delete_alert(alert_id)