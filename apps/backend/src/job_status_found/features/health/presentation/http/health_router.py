"""The health feature's HTTP surface: every health controller, tagged `health`.

`app/app.py` mounts it without a version prefix, so probes keep one path
across API versions. Each endpoint lives in its own controller module; add its
router here.
"""

from fastapi import APIRouter

from job_status_found.features.health.presentation.http.health_controller import (
    router as health_controller_router,
)

router = APIRouter(tags=["health"])
router.include_router(health_controller_router)
