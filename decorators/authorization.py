from functools import wraps

from fastapi import Request, status
from fastapi.responses import RedirectResponse


def require_cookie_authorization(cookie_key: str):

    def decorator(to_be_authorized):
        @wraps(to_be_authorized)
        async def wrapper(request: Request, *args, **kwargs):
            if request.cookies.get(cookie_key):
                result = await to_be_authorized(request, *args, **kwargs)

            else:
                result = RedirectResponse(
                    url='/',
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            return result
        return wrapper
    return decorator
