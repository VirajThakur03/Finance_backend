import logging
from typing import Annotated, List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services import analytics as analytics_service
from app.dependencies.auth import analyst_required, CurrentUser
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Type alias for brevity
Database = Annotated[AsyncSession, Depends(get_session)]

@router.get("/summary", dependencies=[analyst_required])
async def get_records_summary(
    db: Database,
    user: CurrentUser # Any authenticated user
) -> Dict:
    """
    Returns an overview of total income, expenses, and current balance.
    Restricted to Analysts and Administrators.
    """
    logger.info(f"Generating summary for User ID: {user.id}")
    
    income = await analytics_service.get_total_income(db, user.id)
    expenses = await analytics_service.get_total_expenses(db, user.id)
    
    return {
        "total_income": income,
        "total_expenses": expenses,
        "current_balance": round(income - expenses, 2)
    }

@router.get("/categories", response_model=List[Dict], dependencies=[analyst_required])
async def get_category_breakdown(
    db: Database,
    user: CurrentUser
) -> List[Dict]:
    """
    Retrieves the distribution of finances across different categories.
    """
    logger.info(f"Generating category breakdown for User ID: {user.id}")
    return await analytics_service.get_category_breakdown(db, user.id)

@router.get("/monthly", response_model=List[Dict], dependencies=[analyst_required])
async def get_monthly_summary(
    db: Database,
    user: CurrentUser
) -> List[Dict]:
    """
    Provides a month-over-month trend analysis of income and expenses.
    """
    logger.info(f"Generating monthly history for User ID: {user.id}")
    return await analytics_service.get_monthly_summary(db, user.id)

@router.get("/recent", response_model=List[Dict], dependencies=[analyst_required])
async def get_recent_transactions(
    db: Database,
    user: CurrentUser
) -> List[Dict]:
    """
    Fetches the most recent transaction activity.
    """
    logger.info(f"Fetching recent activity history for User ID: {user.id}")
    return await analytics_service.get_recent_transactions(db, user.id)
