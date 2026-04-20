import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.branch import Branch
from app.schemas.branch import BranchCreate

async def create_branch(db: AsyncSession, branch_in: BranchCreate) -> Branch:
    """Creates a new restaurant branch."""
    db_branch = Branch(**branch_in.model_dump())
    db.add(db_branch)
    await db.commit()
    await db.refresh(db_branch)
    return db_branch

async def get_branches(db: AsyncSession) -> List[Branch]:
    """Retrieves all branches."""
    result = await db.execute(select(Branch))
    return list(result.scalars().all())

async def get_branch(db: AsyncSession, branch_id: uuid.UUID) -> Branch | None:
    """Retrieves a specific branch by ID."""
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    return result.scalars().first()