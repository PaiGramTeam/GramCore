from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import func, BigInteger, JSON
from sqlmodel import Column, DateTime, Field, SQLModel, Integer

__all__ = "HistoryData"


class HistoryData(SQLModel, table=True):
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")
    id: Optional[int] = Field(default=None, sa_column=Column(Integer(), primary_key=True, autoincrement=True))
    user_id: int = Field(sa_column=Column(BigInteger(), primary_key=True, index=True))
    data_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger()))
    time_created: Optional[datetime] = Field(
        sa_column=Column(DateTime, server_default=func.now())  # pylint: disable=E1102
    )
    time_updated: Optional[datetime] = Field(sa_column=Column(DateTime, onupdate=func.now()))  # pylint: disable=E1102
    type: int = Field(sa_column=Column(Integer(), primary_key=True))
    data: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON))
