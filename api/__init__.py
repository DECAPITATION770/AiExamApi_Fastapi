from fastapi import APIRouter, Depends, Body
from . import schemas, services
from . import middleware

router = APIRouter(
    prefix="/api/scripts",
    dependencies=[Depends(middleware.auth_required)]
)

@router.post("/create", response_model=schemas.ScriptResponse, tags=["Main"], description="Create script")
async def create_script(body: schemas.CreateScriptSchema = Depends()):
    return await services.generate_script(name=body.name, max_used=body.max_used, status=body.status)

@router.patch("/{name}/change_status", response_model=schemas.ScriptResponse, tags=["Main"], description="Change script status")
async def change_script_status(name: str, body: schemas.ChangeScriptStatusSchema = Depends()):
    return await services.change_status(name=name, status_value=body.status)

@router.patch("/{name}/change_first_seen", response_model=schemas.ScriptResponse, tags=["Test"], description="Change first_seen")
async def change_script_first_seen(name: str, body: schemas.ChangeScriptFirstSeenSchema = Depends()):
    return await services.change_first_seen(name=name, first_seen=body.first_seen)

@router.patch("/{name}/change_fingerprint", response_model=schemas.ScriptResponse, tags=["Test"], description="Change fingerprint")
async def change_script_fingerprint(name: str, body: schemas.ChangeScriptFingerprintSchema = Depends()):
    return await services.change_fingerprint(name=name, fingerprint=body.fingerprint)

@router.get("/{name}/get", response_model=schemas.ScriptResponse, tags=["Main"], description="Get script")
async def get_script(name: str):
    return await services.get_script_by_name(name=name)

@router.patch("/{name}/change_status_for_users", response_model=schemas.ScriptResponse, tags=["Main"], description="Change script status for users")
async def change_script_status_for_users(name: str, body: schemas.ChangeScriptStatusForUsersSchema = Depends()):
    return await services.change_status_for_users(name=name, status_value=body.status)

@router.get("/{name}/change_status_for_users", response_model=schemas.ScriptResponse, tags=["Main"], description="Change script status for users")
async def change_script_status_for_users(name: str):
    return await services.check_change_status_for_users(name=name)