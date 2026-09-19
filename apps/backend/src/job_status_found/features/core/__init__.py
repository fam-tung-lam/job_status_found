"""Core feature: code that several features or the application shell share.

This facade is the only path another feature or `app/` imports core from.
Core imports no other feature and nothing from `app/`.
"""

from job_status_found.features.core.app_settings import AppSettings, get_app_settings
from job_status_found.features.core.application.failures.email_delivery_failure import (
    EmailDeliveryFailure,
)
from job_status_found.features.core.application.ports.unit_of_work import UnitOfWork
from job_status_found.features.core.di import (
    get_smtp_email_sender_client,
    get_unit_of_work,
    get_utc_now,
)
from job_status_found.features.core.infrastructure.clients.smtp_email_sender_client import (
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
    problem_details_openapi_content,
    problem_details_response,
)
from job_status_found.features.core.presentation.http.schemas.invalid_input_problem_details_response import (  # noqa: E501
    InvalidInputProblemDetailsResponse,
)
from job_status_found.features.core.presentation.http.schemas.problem_details_response import (
    ProblemDetailsResponse,
)

__all__ = [
    "PROBLEM_JSON_MEDIA_TYPE",
    "AppSettings",
    "Base",
    "EmailDeliveryFailure",
    "InvalidInputProblemDetailsResponse",
    "IpAddress",
    "JsonObject",
    "ProblemDetailsFastAPI",
    "ProblemDetailsResponse",
    "SmtpEmailSenderClient",
    "SmtpSecurity",
    "SurrogateKey",
    "UnitOfWork",
    "get_app_settings",
    "get_database_session",
    "get_smtp_email_sender_client",
    "get_unit_of_work",
    "get_utc_now",
    "handle_request_validation_error",
    "open_database",
    "problem_details_openapi_content",
    "problem_details_response",
    "settings_config",
]
