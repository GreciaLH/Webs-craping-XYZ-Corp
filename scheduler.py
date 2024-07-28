from apscheduler.schedulers.blocking import BlockingScheduler
from scraper import scrape_quotes
import logging
import signal
import sys

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    logger.info("Signal received, shutting down scheduler...")
    scheduler.shutdown()
    sys.exit(0)

def main():
    global scheduler
    scheduler = BlockingScheduler()

    # Programa la tarea para que se ejecute cada día a las 2:00 AM
    scheduler.add_job(scrape_quotes, 'interval', days=1, start_date='2023-01-01 02:00:00')

    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
        scheduler.shutdown()

if __name__ == '__main__':
    main()
