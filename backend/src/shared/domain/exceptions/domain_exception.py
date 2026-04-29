class DomainError(Exception):
    code: str = "DOMAIN_ERROR"


class InvalidInputError(DomainError):
    code = "INVALID_INPUT"


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ForbiddenError(DomainError):
    code = "FORBIDDEN"


class ConflictError(DomainError):
    code = "CONFLICT"


class UpstreamError(DomainError):
    code = "UPSTREAM_ERROR"
