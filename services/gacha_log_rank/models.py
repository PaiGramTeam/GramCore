import enum
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import func, BigInteger, JSON
from sqlmodel import Column, DateTime, Enum, Field, SQLModel, Integer

__all__ = ("GachaLogRank", "GachaLogTypeEnum", "GachaLogQueryTypeEnum")


class GachaLogTypeEnum(int, enum.Enum):
    CHARACTER = 0  # 角色
    WEAPON = 1  # 武器
    DEFAULT = 2  # 常驻
    DEFAULT_WEAPON = 3  # 常驻武器
    HUN = 4  # 集录
    PET = 5  # 邦布


class GachaLogQueryTypeEnum(str, enum.Enum):
    TOTAL = "score_1"
    FIVE_STAR_AVG = "score_2"
    UP_STAR_AVG = "score_3"
    NO_WARP = "score_4"


class GachaLogRank(SQLModel, table=True):
    __tablename__ = "gacha_log_rank"
    __table_args__ = dict(mysql_charset="utf8mb4", mysql_collate="utf8mb4_general_ci")
    id: Optional[int] = Field(default=None, sa_column=Column(Integer(), primary_key=True, autoincrement=True))
    player_id: int = Field(sa_column=Column(BigInteger(), primary_key=True))
    type: GachaLogTypeEnum = Field(sa_column=Column(Enum(GachaLogTypeEnum), primary_key=True))
    score_1: int = Field(sa_column=Column(BigInteger(), default=0))
    """总抽数"""
    score_2: int = Field(sa_column=Column(BigInteger(), default=0))
    """五星平均"""
    score_3: int = Field(sa_column=Column(BigInteger(), default=0))
    """up 平均"""
    score_4: int = Field(sa_column=Column(BigInteger(), default=0))
    """小保底不歪概率"""
    score_5: int = Field(sa_column=Column(BigInteger(), default=0))
    """保留字段"""
    data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    time_created: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, server_default=func.now())  # pylint: disable=E1102
    )
    time_updated: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime, onupdate=func.now())
    )  # pylint: disable=E1102

    def update_by_new(self, new_ins: "GachaLogRank"):
        self.score_1 = new_ins.score_1
        self.score_2 = new_ins.score_2
        self.score_3 = new_ins.score_3
        self.score_4 = new_ins.score_4
        self.score_5 = new_ins.score_5
        self.data = new_ins.data
        self.time_updated = datetime.now()
