"""Main entry point"""
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from sentry_asgi import SentryMiddleware

from app.api.api_v1.api import api_router
from app.core import config
from app.db.session import SessionScope

# Sentry configuration, logging service
if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        environment=config.FASTAPI_ENV,
        integrations=[
            SqlalchemyIntegration(),
            CeleryIntegration()
        ]
    )

app = FastAPI(title=config.PROJECT_NAME, openapi_url=f"{config.API_V1_STR}/openapi.json")

# CORS
origins = []

# TODO: decorator middleware?
# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),

# TODO: decorator middleware?
# catching errors with Sentry
app.add_middleware(SentryMiddleware)

app.include_router(api_router, prefix=config.API_V1_STR)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)

    try:
        request.state.db = SessionScope
        response = await call_next(request)
    finally:
        # clean exit in case of error
        request.state.db.close()
    return response
