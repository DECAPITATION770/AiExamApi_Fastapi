from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from starlette.responses import Response

from api import services
from api import validators
from api import crud
from api import models
from core.configs import settings

from . import schemas as app_schemas
from . import BASE_SCRIPT
from . import services as app_services
from . import utils
from . import image2text


router = APIRouter()


@router.get("/script/{name}", description="Get script, for front (import script)", tags=["Frontend"])
async def get_script_js(name: str):
    script = await crud.get_script_by_name(name)

    if not script:
        return Response(status_code=500)

    if script.status != models.ScriptStatus.ACTIVE:
        return Response(status_code=500)

    try:
        await validators.validate_used(script)
    except HTTPException as e:
        return Response(status_code=500)

    try:
        await validators.validate_first_seen(script)
    except HTTPException as e:
        return Response(status_code=500)

    return Response(
        content=BASE_SCRIPT,
        media_type="application/javascript",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )

@router.post("/check/{name}", tags=["Frontend"])
async def check_answer(
        name: str,
        fingerprint: str = Form(...),
        image: UploadFile = File(None),
):
    script = await crud.get_script_by_name(name)

    if not script:
        return Response(status_code=500)

    if len(fingerprint) < settings.MIN_FINGERPRINT_LEN:
        return Response(status_code=500)

    __valid_fs = await validators.validate_first_seen(script)
    __valid_mu = await validators.validate_used(script)
    __valid_fp = validators.validate_fingerprint(script, fingerprint)
    __valid_im = validators.image_validator(image)

    __change_fs = await crud.change_first_seen(script)
    __change_fp = await crud.change_fingerprint(script, fingerprint)
    __change_u = await crud.change_used(script)

    saved_image_full_path, image_path = await utils.save_image(image, name_prefix=name)
    answer = await crud.create_answer_for_script(script, answer_path=image_path)

    image64 = utils.image2base64(saved_image_full_path)
    answer_output = image2text.solve_task(image64)

    __change_ao = await crud.change_answer_output(answer, answer_output)

    print(answer_output)

    return Response(status_code=200, content=answer_output)














