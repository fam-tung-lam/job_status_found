"""The auth feature's HTTP surface: every auth controller under `/auth`.

`app/app.py` mounts this versioned router under `/v1`. Each endpoint lives in its own
`<operation>_controller.py`; add its router here.
"""

from fastapi import APIRouter

from job_status_found.features.auth.presentation.http.v1.confirm_email_verification_controller import (  # noqa: E501
    router as confirm_email_verification_router,
)
from job_status_found.features.auth.presentation.http.v1.get_current_user_controller import (
    router as get_current_user_router,
)
from job_status_found.features.auth.presentation.http.v1.refresh_session_controller import (
    router as refresh_session_router,
)
from job_status_found.features.auth.presentation.http.v1.resend_email_verification_controller import (  # noqa: E501
    router as resend_email_verification_router,
)
from job_status_found.features.auth.presentation.http.v1.sign_in_controller import (
    router as sign_in_router,
)
from job_status_found.features.auth.presentation.http.v1.sign_out_controller import (
    router as sign_out_router,
)
from job_status_found.features.auth.presentation.http.v1.sign_up_controller import (
    router as sign_up_router,
)

public_router = APIRouter(prefix="/auth", tags=["auth"])
"""Session-establishment endpoints that intentionally allow anonymous requests."""

public_router.include_router(sign_up_router)
public_router.include_router(confirm_email_verification_router)
public_router.include_router(resend_email_verification_router)
public_router.include_router(sign_in_router)
public_router.include_router(refresh_session_router)
public_router.include_router(sign_out_router)

router = APIRouter(prefix="/auth", tags=["auth"])
"""Authenticated auth endpoints included under the application's default guard."""

router.include_router(get_current_user_router)
