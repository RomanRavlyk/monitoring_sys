from typing import List
from fastapi import APIRouter, Depends
from deps import get_alert_service, has_alert_object_permission, verify_jwt, has_admin_permission
from services.alert import AlertService
from schemas.alert import AlertSchema, AlertSchemaResponse

router = APIRouter(tags=["Alert"])

@router.get("/alerts")
async def get_alerts(token = Depends(verify_jwt), alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.get_alerts(int(token["sub"]))

@router.get("/alerts/assigned", response_model=List[AlertSchemaResponse])
async def get_assigned_alerts(token = Depends(verify_jwt), alert_service: AlertService = Depends(get_alert_service)):
    user_id = int(token["sub"])
    return await alert_service.get_assigned_alerts(user_id)

@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: int, is_owner = Depends(has_alert_object_permission),  alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.get_alert_by_id(alert_id)

@router.post("/alerts/{alert_id}/complete")
async def complete_alert(alert_id: int, token = Depends(has_alert_object_permission), alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.complete_alert(alert_id, int(token["sub"]))

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, is_owner = Depends(has_alert_object_permission), alert_service: AlertService = Depends(get_alert_service)):
    return await alert_service.delete_alert(alert_id)

@router.get("/admin/alerts/{user_id}", response_model=List[AlertSchemaResponse])
async def get_alerts_by_user_id(user_id: int,
                                alert_service: AlertService = Depends(get_alert_service),
                                is_admin = Depends(has_admin_permission)
                                ):
    return await alert_service.get_alerts_by_user(user_id)