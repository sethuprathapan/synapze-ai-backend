from fastapi import APIRouter, Request

router = APIRouter(tags=["Operations"])

REQUEST_COUNT = 0
ERROR_COUNT = 0


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/metrics")
def metrics():
    return {
        "requests_total": REQUEST_COUNT,
        "errors_total": ERROR_COUNT,
    }


async def metrics_middleware(request: Request, call_next):
    global REQUEST_COUNT, ERROR_COUNT
    REQUEST_COUNT += 1
    response = await call_next(request)
    if response.status_code >= 500:
        ERROR_COUNT += 1
    return response
