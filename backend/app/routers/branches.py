import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.branch import OutletCreate, OutletResponse
from app.services import branch_service
from app.routers.deps import require_roles
from app.models.enums import UserRole

router = APIRouter()


@router.post("/", response_model=OutletResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(branch_in: OutletCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_roles([UserRole.owner]))):
    return await branch_service.create_branch(db, branch_in)


@router.get("/", response_model=List[OutletResponse])
async def list_branches(db: AsyncSession = Depends(get_db)):
    return await branch_service.get_branches(db)


@router.get("/{branch_id}", response_model=OutletResponse)
async def get_branch(branch_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    branch = await branch_service.get_branch(db, branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outlet not found")
    return branch
