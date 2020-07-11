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

default_error_response = lambda x: Response(
    error.replace(b"%S%", x.encode()),
    status=429,
    headers={"x-rate-limit": "1", "x-time-left": x},
)


def guard(
    number_of_requests=10,
    *,
    per=3,
    units=SECONDS,
    limit_response=default_error_response,
    ip_resolver="heroku",
    ban_time=0,
):
    time_interval = per * units

    kwargs = {
        "limit": time_interval,
        "min_requests": number_of_requests,
        "ban_time": ban_time,
    }
    if ip_resolver == "heroku":
        kwargs["use_heroku_ip_resolver"] = True
    else:
        kwargs["ip_resolver"] = ip_resolver

    guard = Gate(**kwargs)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            is_banned, time_left = guard.guard(request)
            if is_banned:
                return default_error_response(f"{int(time_left)}")
            return fn(*args, **kwargs)

        return wrapper

    return decorator
