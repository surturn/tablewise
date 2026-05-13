import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.branch import Outlet
from app.schemas.branch import OutletCreate


async def create_branch(db: AsyncSession, branch_in: OutletCreate) -> Outlet:
    db_obj = Outlet(**branch_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_branches(db: AsyncSession) -> list[Outlet]:
    result = await db.execute(select(Outlet).where(Outlet.is_active.is_(True)))
    return list(result.scalars().all())


async def get_branch(db: AsyncSession, branch_id: uuid.UUID) -> Outlet | None:
    return await db.get(Outlet, branch_id)
