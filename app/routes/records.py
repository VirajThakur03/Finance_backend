import logging
from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.session import get_session
from app.models.record import FinancialRecord, RecordType
from app.models.user import User
from app.schemas.record import RecordCreate, RecordOut, RecordUpdate, TransactionType
from app.dependencies.auth import AdminUser, FinancialAnalyst, CurrentUser

logger = logging.getLogger(__name__)
router = APIRouter()

# Type alias for brevity
Database = Annotated[AsyncSession, Depends(get_session)]

@router.post("/", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
async def create_new_record(
    record_data: RecordCreate,
    db: Database,
    admin_user: AdminUser # RBAC: Creation restricted to admins
) -> FinancialRecord:
    """
    Creates a new financial record. Only administrators have write access.
    """
    logger.info(f"Admin ID {admin_user.id} is creating a new {record_data.type} record")
    
    new_record = FinancialRecord(
        **record_data.model_dump(),
        user_id=admin_user.id
    )
    db.add(new_record)
    await db.flush()
    
    logger.info(f"Successfully created record ID: {new_record.id}")
    return new_record

@router.get("/", response_model=List[RecordOut])
async def list_records(
    db: Database,
    current_user: CurrentUser, # Any authenticated user
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    record_type: Optional[TransactionType] = None,
    category: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None
) -> List[FinancialRecord]:
    """
    Retrieves a list of records with support for filtering and pagination.
    Analysts see all data; regular users only see their own entries.
    """
    query = select(FinancialRecord)
    
    # Apply ownership filters based on role
    if current_user.role not in ["admin", "analyst"]:
        query = query.where(FinancialRecord.user_id == current_user.id)
        
    filters = []
    if record_type:
        filters.append(FinancialRecord.type == record_type)
    if category:
        filters.append(FinancialRecord.category.ilike(f"%{category}%")) # Support fuzzy search
    if since:
        filters.append(FinancialRecord.date >= since)
    if until:
        filters.append(FinancialRecord.date <= until)
        
    if filters:
        query = query.where(and_(*filters))
        
    query = query.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit)
    
    records = (await db.execute(query)).scalars().all()
    logger.info(f"Retrieved {len(records)} records for user {current_user.email}")
    return records

@router.get("/{record_id}", response_model=RecordOut)
async def get_record_by_id(
    record_id: int,
    db: Database,
    current_user: CurrentUser
) -> FinancialRecord:
    """
    Fetches details for a specific record. Strict ownership checking in place.
    """
    record_stmt = select(FinancialRecord).where(FinancialRecord.id == record_id)
    record = (await db.execute(record_stmt)).scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Requested transaction record not found.")
    
    # Ownership verification
    if current_user.role not in ["admin", "analyst"] and record.user_id != current_user.id:
        logger.warning(f"Unauthorized access attempt to Record ID {record_id} by User {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to access this record."
        )
        
    return record

@router.put("/{record_id}", response_model=RecordOut)
async def update_record_details(
    record_id: int,
    update_data: RecordUpdate,
    db: Database,
    admin_user: AdminUser # RBAC: Updates restricted to admins
) -> FinancialRecord:
    """
    Modifies an existing record. Exclusive to administrators.
    """
    record_stmt = select(FinancialRecord).where(FinancialRecord.id == record_id)
    record = (await db.execute(record_stmt)).scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Transaction record not found.")
        
    updates = update_data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(record, key, value)
        
    db.add(record)
    logger.info(f"Admin ID {admin_user.id} updated Record ID: {record_id}")
    return record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record_entry(
    record_id: int,
    db: Database,
    admin_user: AdminUser # RBAC: Deletion restricted to admins
):
    """
    Permanently removes a record from the history.
    """
    record_stmt = select(FinancialRecord).where(FinancialRecord.id == record_id)
    record = (await db.execute(record_stmt)).scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="Transaction record not found.")
        
    await db.delete(record)
    logger.info(f"Admin ID {admin_user.id} deleted Record ID: {record_id}")
    return None
