"""Failure raised when an account lacks a required stored role."""


class RequiredUserRoleNotGrantedFailure(Exception):
    """The account's stored role does not grant the requested operation."""
