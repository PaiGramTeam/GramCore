from datetime import datetime, timedelta
from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from gram_core.base_service import BaseService
from gram_core.dependence.database import Database
from gram_core.services.groups.models import GroupDataBase as Group

__all__ = ("GroupRepository",)


class GroupRepository(BaseService.Component):
    def __init__(self, database: Database):
        self.engine = database.engine

    async def get_by_chat_id(self, chat_id: int) -> Optional[Group]:
        async with AsyncSession(self.engine) as session:
            statement = select(Group).where(Group.chat_id == chat_id)
            results = await session.exec(statement)
            return results.first()

    async def add(self, group: Group):
        async with AsyncSession(self.engine) as session:
            session.add(group)
            await session.commit()

    async def update(self, group: Group) -> Group:
        async with AsyncSession(self.engine) as session:
            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    async def remove(self, group: Group):
        async with AsyncSession(self.engine) as session:
            await session.delete(group)
            await session.commit()

    async def get_all(
        self,
        is_banned: Optional[bool] = None,
        is_left: Optional[bool] = None,
        is_ignore: Optional[bool] = None,
    ) -> List[Group]:
        async with AsyncSession(self.engine) as session:
            statement = select(Group)
            if is_banned is not None:
                statement = statement.where(Group.is_banned == is_banned)
            if is_left is not None:
                statement = statement.where(Group.is_left == is_left)
            if is_ignore is not None:
                statement = statement.where(Group.is_ignore == is_ignore)
            results = await session.exec(statement)
            return results.all()

    async def get_no_need_update(self, limit: int = 10) -> List[Group]:
        async with AsyncSession(self.engine) as session:
            is_left = False
            is_banned = False
            statement = (
                select(Group)
                .where(Group.is_left == is_left)
                .where(Group.is_banned == is_banned)
                .where((Group.updated_at + timedelta(days=1)) > datetime.now())
            )
            if limit:
                statement = statement.limit(limit)
            results = await session.exec(statement)
            return results.all()
