from time import time


def ban_for(number: int, units: int):
    return BanFor(number * units)


def no_ban(number: int, units):
    return BanFor(0)


class BanFor(object):
    def __init__(self, time_period: int):
        self._allow_on = time() + time_period

    def is_banned(self) -> bool:
        return time() < self._allow_on

    def time_left(self) -> int:
        return self._allow_on - time()

