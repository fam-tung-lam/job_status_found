"""The auth feature's HTTP surface: every auth controller under `/auth`.

`app/app.py` mounts it under `/v1`. Each endpoint lives in its own
`<operation>_controller.py`; add its router here.
"""

from fastapi import APIRouter

from job_status_found.features.auth.presentation.http.sign_up_controller import (
    router as sign_up_router,
)

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(sign_up_router)
