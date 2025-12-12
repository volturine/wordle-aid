import datetime

from fastapi import APIRouter

router = APIRouter(tags=['health'])


@router.get('/health')
async def healthcheck() -> dict[str, str]:
    """Lightweight healthcheck endpoint for readiness/liveness probes."""
    return {
        'status': 'ok',
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
    }
