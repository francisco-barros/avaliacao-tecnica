from redis import Redis


class Cache:
    def __init__(self) -> None:
        self.client: Redis | None = None

    def init_app(self, app) -> None:
        self.client = Redis.from_url(app.config["REDIS_URL"], decode_responses=True)

    def get(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ex: int | None = None):
        if not self.client:
            return None
        try:
            return self.client.set(key, value, ex=ex)
        except Exception:
            return None

    def delete(self, key: str):
        if not self.client:
            return None
        try:
            return self.client.delete(key)
        except Exception:
            return None

