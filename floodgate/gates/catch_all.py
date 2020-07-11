from .limit_strategies import BanFor
from time import time
from math import floor


dummy = BanFor(0)


class Gate:
    def __init__(
        self,
        *,
        ip_resolver=None,
        use_heroku_ip_resolver=False,
        limit=3,
        max_size=3000,
        min_requests=10,
        ban_time: int = 0,
    ):
        if use_heroku_ip_resolver:

            def resolver(request):
                return request.headers.get("x-forwarded-for").split(",")[-1].strip()

            self._ip_resolver = resolver

        else:
            default = lambda x: (
                getattr(x, "remote_addr", None) or x.headers.get("x-forwarded-for")
            )
            self._ip_resolver = ip_resolver or default

        self._ip_addresses = []
        self._request_log = {}
        self.max_size = max_size
        self.limit = limit
        self.min_requests = min_requests
        self.ban_time = ban_time

    def _remove_first_ip(self):
        ip = self._ip_addresses.pop(0)
        try:
            del self._request_log[ip]
        except:
            pass

    def is_offending(self, logs: tuple, ip: str):
        ban = logs[1]
        if ban and ban.is_banned():
            return (True, ban.time_left())

        last_request = time()
        request_timestamps = logs[0]
        request_timestamps.append(last_request)
        if len(request_timestamps) == self.min_requests + 1:
            first = request_timestamps.pop(0)
            if floor(last_request - first) <= self.limit:
                self._request_log[ip] = (logs[0], BanFor(self.ban_time))
                return (True, logs[1].time_left())
            return (False, None)
        else:
            return (False, None)

    def guard(self, request):
        ip_address = self._ip_resolver(request)
        try:
            previous_requests = self._request_log[ip_address]
            return self.is_offending(previous_requests, ip_address)

        except KeyError:
            while len(self._ip_addresses) >= self.max_size:
                self._remove_first_ip()
            self._ip_addresses.append(ip_address)
            self._request_log[ip_address] = ([time()], dummy)
            return False
