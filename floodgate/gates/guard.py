from functools import wraps
from typing import Dict
from flask import Response, request

from .limit_strategies import ban_for, no_ban, BanFor
from .units import DAYS, HOURS, MINUTES, SECONDS
from .catch_all import Gate
from json import dumps

error = dumps(
    {"error": "You have been rate limited, try again in %S% seconds"}
).encode()


def default_error_response(t):
    x = f"{int(t)}"
    return Response(
        error.replace(b"%S%", x.encode()),
        status=429,
        headers={"x-rate-limit": "1", "x-time-left": x},
    )


def guard(
    request_count=10,
    *,
    per=3,
    units=SECONDS,
    limit_response=default_error_response,
    ip_resolver="heroku",
    ban_time=0,
):
    time_interval = per * units

    kwargs = {
        "per": time_interval,
        "units": units,
        "request_count": request_count,
        "ban_time": ban_time,
        "ip_resolver": ip_resolver,
    }

    guard = Gate(**kwargs)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            is_banned, time_left = guard.guard(request)
            if is_banned:
                return limit_response(time_left)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
