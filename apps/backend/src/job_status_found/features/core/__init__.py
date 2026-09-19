"""Core feature: code that several features or the application shell share.

This facade is the only path another feature or `app/` imports core from.
Core imports no other feature and nothing from `app/`.
"""

from job_status_found.features.core.app_settings import AppSettings, get_settings
from job_status_found.features.core.application.ports.clock import Clock
from job_status_found.features.core.application.ports.unit_of_work import UnitOfWork
from job_status_found.features.core.di import (
    get_clock,
    get_smtp_email_sender_client,
    get_unit_of_work,
)
from job_status_found.features.core.infrastructure.clients.smtp_email_sender_client import (
    EmailDeliveryFailure,
    SmtpEmailSenderClient,
    SmtpSecurity,
)
from job_status_found.features.core.infrastructure.db.db import (
    Base,
    IpAddress,
    JsonObject,
    SurrogateKey,
    get_database_session,
    open_database,
)
from job_status_found.features.core.infrastructure.settings_config import settings_config
from job_status_found.features.core.presentation.http.core_exception_handlers import (
    handle_request_validation_error,
)
from job_status_found.features.core.presentation.http.problem_details_fastapi import (
    ProblemDetailsFastAPI,
)
from job_status_found.features.core.presentation.http.problem_details_responses import (
    PROBLEM_JSON_MEDIA_TYPE,
    problem_details_content,
    problem_details_response,
)
from job_status_found.features.core.presentation.http.schemas.invalid_input_problem_details import (
    InvalidInputProblemDetails,
)
from job_status_found.features.core.presentation.http.schemas.problem_details import (
    ProblemDetails,
)

__all__ = [
    "PROBLEM_JSON_MEDIA_TYPE",
    "AppSettings",
    "Base",
    "Clock",
    "EmailDeliveryFailure",
    "InvalidInputProblemDetails",
    "IpAddress",
    "JsonObject",
    "ProblemDetails",
    "ProblemDetailsFastAPI",
    "SmtpEmailSenderClient",
    "SmtpSecurity",
    "SurrogateKey",
    "UnitOfWork",
    "get_clock",
    "get_database_session",
    "get_settings",
    "get_smtp_email_sender_client",
    "get_unit_of_work",
    "handle_request_validation_error",
    "open_database",
    "problem_details_content",
    "problem_details_response",
    "settings_config",
]
