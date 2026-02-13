from app.celery.app import celery
import logging
logger = logging.getLogger(__name__)


@celery.task
def send_welcome_email(email: str):
    logger.info(f"Sending welcome email to {email}")
    # Здесь будет реальная отправка, когда подключу SMTP
    return f"Email sent to {email}"
