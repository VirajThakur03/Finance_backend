import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select

from app.db.session import SessionFactory
from app.models.user import User
from app.models.record import FinancialRecord, RecordType
from app.core.security import get_password_hash

# Configure logging for script execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def populate_dev_database():
    """
    Utility script for initializing the developer environment.
    Creates structured test accounts and financial history.
    """
    logger.info("Initializing developer data push...")
    
    async with SessionFactory() as session:
        # 1. Idempotent Account Initialization
        logger.info("Verifying system users...")
        
        user_definitions = [
            {
                "full_name": "System Administrator",
                "email": "admin@example.com",
                "password": "admin123",
                "role": "admin"
            },
            {
                "full_name": "Financial Analyst",
                "email": "analyst@example.com",
                "password": "analyst123",
                "role": "analyst"
            },
            {
                "full_name": "Standard Viewer",
                "email": "viewer@example.com",
                "password": "viewer123",
                "role": "viewer"
            }
        ]
        
        accounts = []
        for user_data in user_definitions:
            # Check for existing user
            existing_user_stmt = select(User).where(User.email == user_data["email"])
            existing_user = (await session.execute(existing_user_stmt)).scalar_one_or_none()
            
            if existing_user:
                logger.info(f"User {user_data['email']} already exists. Skipping.")
                accounts.append(existing_user)
            else:
                logger.info(f"Creating user {user_data['email']}...")
                new_user = User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"]
                )
                session.add(new_user)
                accounts.append(new_user)
        
        await session.commit()
        
        # Refresh all to obtain primary keys
        for acc in accounts:
            await session.refresh(acc)
            
        admin_id = accounts[0].id
        
        # 2. Activity History Generation
        logger.info(f"Injecting financial legacy for Admin ID {admin_id}...")
        
        # Note: We'll inject records even if users existed, as history can grow.
        # To make records idempotent too, you could check for existence, but usually 
        # for a seed script we just want to add volume.
        history = [
            FinancialRecord(
                amount=7500.0,
                type=RecordType.INCOME,
                category="Salary",
                notes="Primary source: Tech Salary",
                user_id=admin_id,
                date=datetime.now() - timedelta(days=15)
            ),
            FinancialRecord(
                amount=245.50,
                type=RecordType.EXPENSE,
                category="Utilities",
                notes="Cloud Subscription / Home WiFi",
                user_id=admin_id,
                date=datetime.now() - timedelta(days=10)
            ),
            FinancialRecord(
                amount=120.0,
                type=RecordType.EXPENSE,
                category="Food",
                notes="Team Dinner",
                user_id=admin_id,
                date=datetime.now() - timedelta(days=5)
            ),
            FinancialRecord(
                amount=350.0,
                type=RecordType.INCOME,
                category="Investment",
                notes="Dividends: Tech ETFs",
                user_id=admin_id,
                date=datetime.now() - timedelta(days=2)
            ),
            FinancialRecord(
                amount=15.0,
                type=RecordType.EXPENSE,
                category="Transport",
                notes="Bus Fare / Local Commute",
                user_id=admin_id,
                date=datetime.now()
            )
        ]
        
        session.add_all(history)
        await session.commit()
        
        logger.info("Dev environment initialized. Database populated successfully.")

if __name__ == "__main__":
    try:
        asyncio.run(populate_dev_database())
    except KeyboardInterrupt:
        logger.info("Initialization aborted by user.")
    except Exception as e:
        logger.error(f"Critical failure during seeding: {e}", exc_info=True)
