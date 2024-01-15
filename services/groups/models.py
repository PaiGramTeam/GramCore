import enum
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, DateTime, Column, Enum, BigInteger, Integer, TEXT

__all__ = (
    "Group",
    "GroupDataBase",
    "ChatTypeEnum",
)


class ChatTypeEnum(str, enum.Enum):
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


class Group(SQLModel):
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")
    id: Optional[int] = Field(default=None, sa_column=Column(Integer(), primary_key=True, autoincrement=True))
    chat_id: int = Field(sa_column=Column(BigInteger(), unique=True))
    type: ChatTypeEnum = Field(sa_column=Column(Enum(ChatTypeEnum)))
    title: str = Field()
    description: Optional[str] = Field(sa_column=Column(TEXT()))
    username: Optional[str] = Field()
    big_photo_id: Optional[str] = Field()
    small_photo_id: Optional[str] = Field()
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    is_left: int = Field(sa_column=Column(Integer(), default=0))
    is_banned: int = Field(sa_column=Column(Integer(), default=0))


class GroupDataBase(Group, table=True):
    __tablename__ = "groups"
