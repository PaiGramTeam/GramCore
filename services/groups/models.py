import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, DateTime, Column, Enum, BigInteger, Integer, TEXT

__all__ = (
    "Group",
    "GroupDataBase",
    "ChatTypeEnum",
)

if TYPE_CHECKING:
    from telegram import Chat


class ChatTypeEnum(str, enum.Enum):
    SENDER = "sender"
    PRIVATE = "private"
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
    is_ignore: int = Field(sa_column=Column(Integer(), default=0))


class GroupDataBase(Group, table=True):
    __tablename__ = "groups"

    @classmethod
    def from_chat(cls, chat: "Chat") -> "GroupDataBase":
        return cls(
            chat_id=chat.id,
            type=ChatTypeEnum(chat.type),
            title=chat.effective_name,
            description=chat.description,
            username=chat.username,
            big_photo_id=chat.photo.big_file_id if chat.photo else None,
            small_photo_id=chat.photo.small_file_id if chat.photo else None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_left=0,
            is_banned=0,
            is_ignore=0,
        )

    @classmethod
    def from_id(cls, chat_id: int) -> "GroupDataBase":
        return cls(
            chat_id=chat_id,
            type=ChatTypeEnum.PRIVATE,
            title="",
            description=None,
            username=None,
            big_photo_id=None,
            small_photo_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_left=0,
            is_banned=0,
            is_ignore=0,
        )
