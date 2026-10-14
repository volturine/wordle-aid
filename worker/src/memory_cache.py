"""Small in-process caches for definition lookups."""
import asyncio
from collections import OrderedDict


class LruCache:
    def __init__(self, max_entries: int):
        self.max_entries = max_entries
        self._items: OrderedDict = OrderedDict()

    def get(self, key):
        value = self._items.get(key)
        if value is None and key not in self._items:
            return None
        self._items.move_to_end(key)
        return self._items[key]

    def set(self, key, value) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    def __len__(self) -> int:
        return len(self._items)


class TtlCache:
    def __init__(self, max_entries: int, ttl_seconds: float):
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._items: OrderedDict = OrderedDict()

    def get(self, key, now: float):
        item = self._items.get(key)
        if item is None:
            return None
        value, expires = item
        if expires <= now:
            del self._items[key]
            return None
        self._items.move_to_end(key)
        return value

    def set(self, key, value, now: float) -> None:
        self._items[key] = (value, now + self.ttl_seconds)
        self._items.move_to_end(key)
        expired = [stored for stored, (_, expires) in self._items.items() if expires <= now]
        for stored in expired:
            del self._items[stored]
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)

    def __len__(self) -> int:
        return len(self._items)


class InFlight:
    """Share one lookup while the first caller is still waiting."""

    def __init__(self):
        self._waiters: dict[str, asyncio.Future] = {}

    def start(self, key: str):
        existing = self._waiters.get(key)
        if existing is not None:
            return existing, False
        future = asyncio.get_running_loop().create_future()
        self._waiters[key] = future
        return future, True

    def succeed(self, key: str, value) -> None:
        future = self._waiters.pop(key)
        if not future.done():
            future.set_result(value)

    def fail(self, key: str, error: BaseException) -> None:
        future = self._waiters.pop(key)
        if not future.done():
            future.set_exception(error)
        # The leader raises `error` and does not await this future. Retrieve the
        # exception so an unfollowed failure is not reported as never retrieved.
        # A follower that awaits the same future still receives it.
        if not future.cancelled():
            future.exception()


def classify_definition(status: int, payload) -> str:
    """Classify an upstream WordsAPI definitions response.

    WordsAPI uses 404 when it has no entry. A 200 body with a definitions
    array is a finished lookup, including an empty array. Anything else is a
    provider failure and must not be cached.
    """
    if status == 404:
        return 'missing'
    if status != 200 or not isinstance(payload, dict) or not isinstance(payload.get('definitions'), list):
        return 'error'
    return 'ready'
