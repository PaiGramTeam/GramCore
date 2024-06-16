import contextlib
from typing import Optional

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from typing_extensions import Self

from gram_core.base_service import BaseService
from gram_core.config import ApplicationConfig

__all__ = ("InfluxDatabase",)


class InfluxDatabase(BaseService.Dependence):
    @classmethod
    def from_config(cls, config: ApplicationConfig) -> Self:
        return cls(**config.influxdb.dict())

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        token: Optional[str] = None,
        org: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.token = token
        self.org = org
        self.url = f"http://{host}:{port}"
        self.db_client = InfluxDBClientAsync(url=self.url, token=self.token, org=self.org)

    @contextlib.asynccontextmanager
    async def client(self) -> InfluxDBClientAsync:
        yield self.db_client

    async def shutdown(self):
        await self.db_client.close()
