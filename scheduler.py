from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import pytz

scheduler = BlockingScheduler(timezone=pytz.UTC)

def schedule(hour, minute, seconds, fuc, args=None):
 
    scheduler.add_job(
        args=args,
        func=fuc,
        trigger='cron',
        hour=hour,  
        minute=minute,
        second=seconds
    )

    print("Scheduler started, waiting to run the function at 10 PM UTC...")
    
def start_scheduler():
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")