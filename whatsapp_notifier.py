"""
WhatsApp notifier using Green API (green-api.com).
Sends each job as a separate message to a WhatsApp group.
Free tier: 1000 messages/month.
"""
import os
import time
import logging

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GREEN_API_URL = "https://api.green-api.com"


def _send_message(instance_id: str, api_token: str, chat_id: str, text: str) -> bool:
    """Send a single WhatsApp message via Green API. Returns True on success."""
    url = f"{GREEN_API_URL}/waInstance{instance_id}/sendMessage/{api_token}"
    payload = {
        "chatId": chat_id,
        "message": text,
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False


def format_job_message(job: dict) -> str:
    """Format a job dict into the WhatsApp message format."""
    return (
        f"*Job Title:* {job.get('Job Title', '')}\n"
        f"*Company:* {job.get('Company', '')}\n"
        f"*Location:* {job.get('Location', '')}\n"
        f"*Link to the job:* {job.get('Job URL', '')}"
    )


def send_jobs_to_whatsapp(jobs: list[dict]) -> int:
    """
    Send each job as a separate WhatsApp message to the configured group.
    Returns the number of messages successfully sent.
    """
    if not jobs:
        logger.info("WhatsApp: no jobs to send.")
        return 0

    instance_id = os.environ.get("GREEN_API_INSTANCE_ID")
    api_token   = os.environ.get("GREEN_API_TOKEN")
    chat_id     = os.environ.get("WHATSAPP_GROUP_CHAT_ID")

    if not all([instance_id, api_token, chat_id]):
        logger.warning(
            "WhatsApp: missing credentials. Set GREEN_API_INSTANCE_ID, "
            "GREEN_API_TOKEN, and WHATSAPP_GROUP_CHAT_ID."
        )
        return 0

    sent = 0
    for job in jobs:
        message = format_job_message(job)
        success = _send_message(instance_id, api_token, chat_id, message)
        if success:
            sent += 1
            logger.info(f"WhatsApp: sent '{job.get('Job Title')}'")
        else:
            logger.warning(f"WhatsApp: failed to send '{job.get('Job Title')}'")
        # Small delay between messages to avoid rate limiting
        time.sleep(1.5)

    logger.info(f"WhatsApp: {sent}/{len(jobs)} messages sent.")
    return sent
