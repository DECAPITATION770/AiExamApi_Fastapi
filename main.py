from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core import db
from api import router as v1_router
from app.routers import router as app_router

app = FastAPI()

app.exception_handlers.clear()

# @app.exception_handler(StarletteHTTPException)
# async def handle_http_exc(request: Request, exc: StarletteHTTPException):
#     return Response(status_code=500)
#
# @app.exception_handler(Exception)
# async def handle_all_exc(request: Request, exc: Exception):
#     return Response(status_code=500)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": "validation_error",
            "data": None,
            "detail": exc.errors()
        }
    )

app.include_router(v1_router)
app.include_router(app_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await db.init()

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()