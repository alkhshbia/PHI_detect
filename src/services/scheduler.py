import threading
import time
import logging
from datetime import datetime
from src.services.eios_fetcher import EIOSFetcher
from src.services.signal_processor import ArticleProcessor
from src.models.signal import UserConfig

logger = logging.getLogger("scheduler")

class SignalScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        self.interval = 3600  # 1 hour in seconds
        self.last_run_time = None
        self.last_run_status = None  # 'success', 'error', or None
        self.last_run_message = None
        self.next_run_time = None
        self.is_currently_fetching = False

    def start(self):
        """Start the scheduler thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Article scheduler started - will fetch articles every hour")

    def stop(self):
        """Stop the scheduler thread."""
        self.running = False
        self.next_run_time = None
        if self.thread:
            # Don't block indefinitely - just signal the thread to stop
            self.thread = None
        logger.info("Article scheduler stopped")

    def get_status(self):
        """Get detailed scheduler status."""
        return {
            'running': self.running,
            'is_fetching': self.is_currently_fetching,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_run_status': self.last_run_status,
            'last_run_message': self.last_run_message,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'interval_seconds': self.interval
        }

    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._fetch_and_process_signals()
            except Exception as e:
                logger.error(f"Error in scheduled article processing: {e}")
                self.last_run_status = 'error'
                self.last_run_message = str(e)

            # Calculate next run time
            if self.running:
                self.next_run_time = datetime.now() + timedelta(seconds=self.interval)

            # Sleep for the interval, but check periodically if we should stop
            sleep_time = 0
            while sleep_time < self.interval and self.running:
                time.sleep(60)  # Check every minute
                sleep_time += 60

    def _fetch_and_process_signals(self):
        """Fetch and process signals - same logic as manual trigger."""
        logger.info("Starting scheduled article fetch and processing")
        self.is_currently_fetching = True
        self.last_run_time = datetime.now()

        try:
            # Import the app within this method to avoid circular imports
            from src.main import app
            # Push the application context for the duration of the scheduled work
            with app.app_context():
                # Get user-defined tags
                from src.models.signal import db
                with db.session.no_autoflush:
                    tags_config = UserConfig.query.filter_by(key='tags').first()
                    if tags_config and tags_config.value:
                        tags = [tag.strip() for tag in tags_config.value.split(',') if tag.strip()]
                    else:
                        # Default tags if none configured
                        tags = ["ephem emro"]

                logger.info(f"Fetching articles with tags: {tags}")

                # Fetch articles from EIOS with error handling
                try:
                    fetcher = EIOSFetcher()
                    articles = fetcher.fetch_articles(tags)
                except Exception as fetch_error:
                    logger.error(f"EIOS fetch error: {fetch_error}")
                    self.last_run_status = 'error'
                    self.last_run_message = f"EIOS fetch failed: {str(fetch_error)}"
                    return

                if not articles:
                    logger.info("No new articles found during scheduled fetch")
                    self.last_run_status = 'success'
                    self.last_run_message = "No new articles found"
                    return

                # Process articles
                try:
                    processor = ArticleProcessor()
                    processed_articles = processor.process_articles_batch(articles, batch_size=None)

                    # Count potential signals (is_signal = 'Yes')
                    potential_signals_count = sum(1 for article in processed_articles if article.is_signal == 'Yes')

                    self.last_run_status = 'success'
                    self.last_run_message = f"Processed {len(processed_articles)} articles, {potential_signals_count} potential signals"
                    logger.info(f"Scheduled processing complete: {self.last_run_message}")
                except Exception as process_error:
                    logger.error(f"Article processing error: {process_error}")
                    self.last_run_status = 'error'
                    self.last_run_message = f"Processing failed: {str(process_error)}"

        except Exception as e:
            logger.error(f"Error in scheduled article processing: {e}")
            self.last_run_status = 'error'
            self.last_run_message = str(e)
        finally:
            self.is_currently_fetching = False


# Import timedelta for next_run_time calculation
from datetime import timedelta

# Global scheduler instance
scheduler_instance = None

def start_scheduler():
    """Start the global scheduler instance."""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = SignalScheduler()
    scheduler_instance.start()

def stop_scheduler():
    """Stop the global scheduler instance."""
    global scheduler_instance
    if scheduler_instance:
        scheduler_instance.stop()

def is_scheduler_running():
    """Check if the scheduler is running."""
    global scheduler_instance
    return scheduler_instance and scheduler_instance.running

def get_scheduler_status():
    """Get detailed scheduler status."""
    global scheduler_instance
    if scheduler_instance:
        return scheduler_instance.get_status()
    return {
        'running': False,
        'is_fetching': False,
        'last_run_time': None,
        'last_run_status': None,
        'last_run_message': None,
        'next_run_time': None,
        'interval_seconds': 3600
    }

