# Floodgate

A request rate limiter for Flask

# Installation

```
pip install -U floodgate
```

# Usage

Floodgate provides a `guard` decorator:
More about the `ip_resolver` below

```python


from floodgate import guard
from floodgate.gates.units import MINUTES
from flask import Flask

app = Flask(__name__)


def ip_resolver(request):
    return request.headers["x-real-ip"]


def rate_limit_message(time_left: float):
    return f"You have been rate limited for {time_left}" seconds


@app.route("/nospam")
@guard(
    request_count=50,
    per=2,
    units=MINUTES,   # OR per=2*60
    ban_time=5,
    ip_resolver=ip_resolver,
    limit_response=rate_limit_message,
)
def protected_route():
    return some_db.get("data")


@app.route("/limit_but_dont_ban")
@guard(5, per=5, ip_resolver=ip_resolver)
def limited_route():
    return send_from_directory("static", "large_file")


```

If you want to rate limit the entire app you can do something like this:

```python

@app.before_request
@guard(...)
def before_request():
    pass

```

if you want to conditionally limit a route ex: not limit admin users, instead of using a decorator, you can construct the class yourself:

```python
from floodgate import LimitApp
from flask import request
fg = LimitApp(request_count=3, per=3, ip_resolver="heroku", ban_time=4)


@app.route("/files")
def file_serve():
    if user_is_admin():
        return some_file
    else:
        is_limited, ban_data = fg.guard(request)
        if is_limited:
            return f"You have been banned for {ban_data.time_left()} seconds"
        return some_file()
```

# IP Resolver

You're probably going to be running your app behind some sort of reverse proxy
or your PaaS provider has it's own way of dealing with providing your app with the real IP of the user

Floodgate provides one reslover for heroku ( last ip in the x-forwarded-for header )

you can make your own resolver that suits your needs and pass it to the guard.
