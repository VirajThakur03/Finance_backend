from typing import List, Dict
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.record import FinancialRecord, RecordType

async def get_total_income(db: AsyncSession, user_id: int) -> float:
    """Calculates cumulative income for a specific user"""
    query = (
        select(func.sum(FinancialRecord.amount))
        .where(and_(
            FinancialRecord.type == RecordType.INCOME,
            FinancialRecord.user_id == user_id
        ))
    )
    result = (await db.execute(query)).scalar()
    return float(result) if result else 0.0

async def get_total_expenses(db: AsyncSession, user_id: int) -> float:
    """Calculates cumulative expenses for a specific user"""
    query = (
        select(func.sum(FinancialRecord.amount))
        .where(and_(
            FinancialRecord.type == RecordType.EXPENSE,
            FinancialRecord.user_id == user_id
        ))
    )
    result = (await db.execute(query)).scalar()
    return float(result) if result else 0.0

async def get_category_breakdown(db: AsyncSession, user_id: int) -> List[Dict]:
    """Generates an aggregation of expenses grouped by category"""
    query = (
        select(FinancialRecord.category, func.sum(FinancialRecord.amount))
        .where(FinancialRecord.user_id == user_id)
        .group_by(FinancialRecord.category)
    )
    results = (await db.execute(query)).all()
    return [{"category": row[0], "total": round(float(row[1]), 2)} for row in results]

async def get_recent_transactions(db: AsyncSession, user_id: int, limit: int = 5) -> List[FinancialRecord]:
    """Fetches the most recent transaction objects for the dashboard"""
    query = (
        select(FinancialRecord)
        .where(FinancialRecord.user_id == user_id)
        .order_by(FinancialRecord.date.desc())
        .limit(limit)
    )
    return (await db.execute(query)).scalars().all()

async def get_monthly_summary(db: AsyncSession, user_id: int) -> List[Dict]:
    """
    Compiles monthly financial aggregates. 
    Groups data by year/month and splits by income/expense.
    """
    # Optimized grouping using database-level date truncation
    month_truncated = func.date_trunc('month', FinancialRecord.date).label('month')
    query = (
        select(month_truncated, FinancialRecord.type, func.sum(FinancialRecord.amount))
        .where(FinancialRecord.user_id == user_id)
        .group_by(month_truncated, FinancialRecord.type)
        .order_by(month_truncated)
    )
    
    db_results = (await db.execute(query)).all()
    
    # Process flat results into structured monthly buckets
    history = {}
    for month_dt, rec_type, total in db_results:
        month_key = month_dt.strftime("%Y-%m")
        if month_key not in history:
            history[month_key] = {"income": 0.0, "expense": 0.0}
        
        if rec_type == RecordType.INCOME:
            history[month_key]["income"] = round(float(total), 2)
        else:
            history[month_key]["expense"] = round(float(total), 2)
            
    return [{"month": date, **data} for date, data in history.items()]
