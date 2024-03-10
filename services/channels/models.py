from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, DateTime, Column, BigInteger, Integer

__all__ = (
    "ChannelAlias",
    "ChannelAliasDataBase",
)


class ChannelAlias(SQLModel):
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")
    id: Optional[int] = Field(default=None, sa_column=Column(Integer(), primary_key=True, autoincrement=True))
    chat_id: int = Field(sa_column=Column(BigInteger(), unique=True))
    user_id: int = Field(sa_column=Column(BigInteger()))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))


class ChannelAliasDataBase(ChannelAlias, table=True):
    __tablename__ = "channel_alias"
