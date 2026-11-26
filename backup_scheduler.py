import os
import sqlite3
import glob
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'data', 'backups')
MAX_BACKUPS = 14

def run_backup():
    """Copia consistente de la base de datos (WAL-safe) a data/backups/ con timestamp, y elimina backups viejos si supera MAX_BACKUPS."""
    from db import DB_PATH
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = os.path.join(BACKUP_DIR, f'ultrax_auto_{ts}.db')
    src = sqlite3.connect(DB_PATH, timeout=30.0)
    src.execute('PRAGMA busy_timeout=30000')
    dst = sqlite3.connect(dest)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

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
