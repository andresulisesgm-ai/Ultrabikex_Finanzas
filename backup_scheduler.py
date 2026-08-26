import os
import shutil
import glob
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'data', 'backups')
MAX_BACKUPS = 14

def run_backup():
    """Copia la base de datos actual a data/backups/ con timestamp, y elimina backups viejos si supera MAX_BACKUPS."""
    from db import DB_PATH
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(BACKUP_DIR, f'ultrax_auto_{ts}.db')
    shutil.copy2(DB_PATH, dest)

    backups = sorted(glob.glob(os.path.join(BACKUP_DIR, 'ultrax_auto_*.db')))
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        os.remove(oldest)

    print(f"[backup_scheduler] Backup automatico creado: {dest}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_backup, 'cron', hour=3, minute=0)
    scheduler.start()
    return scheduler
