from contextvars import ContextVar


# Context variable to store the access token for each request
auth_token_context: ContextVar[str] = ContextVar('auth_token')
