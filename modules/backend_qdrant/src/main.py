import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import uvicorn

from config.logger import log_request_validation_error, setup_logger
from routes.qdrant_router import router as router_qdrant

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG_DIR = os.path.join(BASE_DIR, "logs")


setup_logger(
    container_name=os.getenv("CONTAINER_NAME", "backend_qdrant"),
    log_dir=os.getenv("LOG_DIR", DEFAULT_LOG_DIR),
    show_log=os.getenv("SHOW_LOG", "true").lower() == "true",
    error_mode=os.getenv("LOG_ERROR_MODE", "full"),
)

logger = logging.getLogger(__name__)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[os.getenv("GLOBAL_RATE_LIMIT", "20/second")],
)

app = FastAPI(title="backend_qdrant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)

app.include_router(router_qdrant)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    log_request_validation_error(
        logger=logger,
        method=request.method,
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        logger.error(
            "HTTP exception | method=%s | path=%s | status_code=%s | detail=%s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled application exception | method=%s | path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def root():
    return {"message": "backend_qdrant is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010, workers=1)
