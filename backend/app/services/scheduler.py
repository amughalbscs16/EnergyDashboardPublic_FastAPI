"""Background scheduler for data updates"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.data_generator import DataGenerator

scheduler = AsyncIOScheduler()

def start_scheduler():
    """Start background jobs"""
    generator = DataGenerator()

    # Update ERCOT data every 5 minutes
    scheduler.add_job(
        generator.update_ercot_data,
        'interval',
        minutes=5,
        id='update_ercot'
    )

    scheduler.start()
    print("Background scheduler started")