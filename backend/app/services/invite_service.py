import secrets
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.invite import InviteToken
from app.models.enums import UserRole
from app.schemas.invite import InviteCreate
from app.models.user import User


async def create_invite(db: AsyncSession, invite_data: InviteCreate, current_user: User) -> InviteToken:
    """
    Creates an invite token. If the creator is an owner, it's auto-approved.
    If the creator is a manager, it requires owner approval.
    """
    token_str = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)
    
    is_approved = current_user.role == UserRole.owner

    new_invite = InviteToken(
        token=token_str,
        role=invite_data.role,
        outlet_id=invite_data.outlet_id,
        expires_at=expires_at,
        is_used=False,
        is_approved=is_approved,
        created_by_id=current_user.id,
        approved_by_id=current_user.id if is_approved else None
    )
    
    db.add(new_invite)
    await db.commit()
    await db.refresh(new_invite)
    
    return new_invite


async def approve_invite(db: AsyncSession, token: str, current_user: User) -> InviteToken:
    """
    Approves a pending invite token. Only owners can do this.
    """
    if current_user.role != UserRole.owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can approve invites")
        
    result = await db.execute(select(InviteToken).where(InviteToken.token == token))
    invite = result.scalars().first()
    
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
        
    if invite.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite is already approved")
        
    invite.is_approved = True
    invite.approved_by_id = current_user.id
    
    await db.commit()
    await db.refresh(invite)
    return invite


async def validate_invite(db: AsyncSession, token: str) -> InviteToken:
    """
    Validates an invite token. Returns the token object if valid, raises HTTPException otherwise.
    """
    result = await db.execute(select(InviteToken).where(InviteToken.token == token))
    invite = result.scalars().first()
    
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite token")
        
    if invite.is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite token has already been used")
        
    if not invite.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite token is pending owner approval")
        
    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite token has expired")
        
    return invite


async def consume_invite(db: AsyncSession, token: str) -> InviteToken:
    """
    Consumes a valid invite token.
    """
    invite = await validate_invite(db, token)
    invite.is_used = True
    await db.commit()
    return invite
