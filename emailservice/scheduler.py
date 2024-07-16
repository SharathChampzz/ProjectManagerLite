import sys, os

# Add the path to the sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from task_processor import TaskProcessor

import logging
from logging.config import dictConfig
import log_config
dictConfig(log_config.logging_config)

logger = logging.getLogger("app")

## Load environment variables - START ##

from dotenv import load_dotenv
load_dotenv()

help_str = """
Required Environment Variables:

- EMAIL_PARSE_INTERVAL: The interval in minutes to parse incoming emails.
- SEND_REMINDER_INTERVAL: The interval in minutes to send reminders.
- REMINDER_INTERVAL_FOR_CRITICAL: The interval in hours to send reminders for critical tasks.
- REMINDER_INTERVAL_FOR_HIGH: The interval in hours to send reminders for high priority tasks.
- REMINDER_INTERVAL_FOR_MEDIUM: The interval in hours to send reminders for medium priority tasks.
- REMINDER_INTERVAL_FOR_LOW: The interval in hours to send reminders for low priority tasks.
- BOT_EMAIL: The email address of the bot.

- UI_BASE_URL: The base URL of the UI. This is used to generate the links in the email.
- API_BASE_URL: The base URL of the API. This is used to communicate with the backend application.
- USER_NAME: The username to communicate with the backend application to upload files and create tasks.
- PASSWORD: The password to communicate with the backend application to upload files and create tasks.
"""

# read environment variables
EMAIL_PARSE_INTERVAL = os.getenv("EMAIL_PARSE_INTERVAL")
SEND_REMINDER_INTERVAL = os.getenv("SEND_REMINDER_INTERVAL")

REMINDER_INTERVAL_FOR_CRITICAL = os.getenv("REMINDER_INTERVAL_FOR_CRITICAL")
REMINDER_INTERVAL_FOR_HIGH = os.getenv("REMINDER_INTERVAL_FOR_HIGH")
REMINDER_INTERVAL_FOR_MEDIUM = os.getenv("REMINDER_INTERVAL_FOR_MEDIUM")
REMINDER_INTERVAL_FOR_LOW = os.getenv("REMINDER_INTERVAL_FOR_LOW")

BOT_EMAIL = os.getenv("BOT_EMAIL")

UI_BASE_URL = os.getenv("UI_BASE_URL")
API_BASE_URL = os.getenv("API_BASE_URL")
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")

if not all([EMAIL_PARSE_INTERVAL, SEND_REMINDER_INTERVAL, REMINDER_INTERVAL_FOR_CRITICAL, REMINDER_INTERVAL_FOR_HIGH, 
            REMINDER_INTERVAL_FOR_MEDIUM, REMINDER_INTERVAL_FOR_LOW, BOT_EMAIL, UI_BASE_URL, API_BASE_URL, USER_NAME, PASSWORD]):
    logger.error(help_str)
    print(help_str)
    raise ValueError("Please set the required environment variables.")

## Load environment variables - END ##

logger.info(f"Email parse interval: {EMAIL_PARSE_INTERVAL} minutes")
logger.info(f"Send reminder interval: {SEND_REMINDER_INTERVAL} minutes")

# check if webservice is running first and retry after 5 seconds till it is up
import requests, time
while True:
    try:
        logger.info(f"Checking if web service is running => {API_BASE_URL}/api")
        response = requests.get(f"{API_BASE_URL}/api")
        if response.status_code == 200:
            logger.info("Web service is running")
            logger.info(response.text)
            break
    except:
        print("Web service is not running. Retrying in 5 seconds...")
        logger.exception("Web service is not running. Retrying in 5 seconds...")
    time.sleep(5)

async def read_incoming_messages():
    logger.info("Reading incoming messages...")
    task_processor = TaskProcessor()
    task_processor.process_incoming_emails(max_results=5, download_email=True)

async def send_reminders():
    logger.info("Sending reminders...")
    task_processor = TaskProcessor()
    task_processor.send_reminders()

async def main():
    scheduler = AsyncIOScheduler()

    logger.info("Adding jobs to scheduler...")
    scheduler.add_job(read_incoming_messages, IntervalTrigger(minutes=int(EMAIL_PARSE_INTERVAL)))
    scheduler.add_job(send_reminders, IntervalTrigger(minutes=int(SEND_REMINDER_INTERVAL)))

    logger.info("Starting scheduler...")
    scheduler.start()

    # Keep the script running to allow the scheduler to execute the tasks
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
