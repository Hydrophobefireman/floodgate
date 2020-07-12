from .limit_strategies import BanFor
from .units import SECONDS
from time import time
from math import floor


dummy = BanFor(0)


class Gate:
    def __init__(
        self,
        request_count=10,
        *,
        ip_resolver=None,
        per=3,
        units=SECONDS,
        max_size=3000,
        ban_time: int = 0,
    ):
        if ip_resolver == "heroku":

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
        self.limit = per * units
        self.request_count = request_count
        self.ban_time = ban_time

    def _remove_first_ip(self):
        ip = self._ip_addresses.pop(0)
        try:
            del self._request_log[ip]
        except:
            pass

    def is_offending(self, logs: tuple, ip: str):
        ban = logs[1]
        last_request = time()
        request_timestamps = logs[0]
        request_timestamps.append(last_request)

        if len(request_timestamps) == self.request_count + 1:
            first = request_timestamps.pop(0)
            if floor(last_request - first) <= self.limit:
                ban = BanFor(self.ban_time)
                self._request_log[ip] = (logs[0], ban)
                return (True, ban.time_left())

            elif ban and ban.is_banned():
                return (True, ban.time_left())

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
            return (False, None)
