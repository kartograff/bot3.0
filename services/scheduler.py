import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.delayed_notifications import DelayedNotificationProcessor
from services.silent_hours import silent_hours_service
from utils.backup import BackupManager
from config import Config

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manages all background tasks."""
    
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.delayed_processor = DelayedNotificationProcessor(bot)
        self.backup_manager = BackupManager({
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        })
    
    async def daily_backup(self):
        """Create automatic daily backup."""
        logger.info("Running daily backup...")
        try:
            self.backup_manager.create_backup(
                backup_type='automatic',
                comment='Ежедневный автоматический бекап'
            )
        except Exception as e:
            logger.exception(f"Daily backup failed: {e}")
    
    async def weekly_cleanup(self):
        """Clean up old backups."""
        logger.info("Cleaning old backups...")
        try:
            self.backup_manager.cleanup_old_backups(keep_days=30)
        except Exception as e:
            logger.exception(f"Backup cleanup failed: {e}")
    
    def start(self):
        """Start all scheduled jobs."""
        # Delayed notifications processing (every minute)
        self.scheduler.add_job(self.delayed_processor.process_pending_notifications, 'interval', minutes=1)
        
        # Daily backup at 3:00 AM
        self.scheduler.add_job(self.daily_backup, 'cron', hour=3, minute=0)
        
        # Weekly backup cleanup (Sunday at 4:00 AM)
        self.scheduler.add_job(self.weekly_cleanup, 'cron', day_of_week='sun', hour=4, minute=0)
        
        self.scheduler.start()
        logger.info("Scheduler started.")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped.")