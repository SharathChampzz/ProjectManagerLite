import requests
from email_helper import EmailHelper
from dotenv import load_dotenv
import os
from enum import Enum
import traceback
import datetime

load_dotenv()

import logging

class TaskStatus(str, Enum):
    OPEN = "OPEN"
    FIXED = "FIXED"
    CLOSED = "CLOSED"
    
class TaskCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TaskProcessor:
    """Class to handle task creation and updating using the API."""
    
    def __init__(self):
        """Initializes the class with the necessary attributes."""
        self.API_BASE_URL   = os.getenv('API_BASE_URL')
        self.UI_BASE_URL    = os.getenv('UI_BASE_URL')
        self.USER_NAME      = os.getenv('USER_NAME')
        self.PASSWORD       = os.getenv('PASSWORD')
        self.BOT_EMAIL      = os.getenv('BOT_EMAIL')
        self.TASK_EDIT_URL  = f'{self.UI_BASE_URL}/tasks/%s/edit'
        
        self.log = logging.getLogger("app") # initialize logger
        
        # Reminder intervals in hours
        self.REMINDER_INTERVALS = {
            TaskCriticality.LOW.value: os.getenv('REMINDER_INTERVAL_FOR_LOW', 48),
            TaskCriticality.MEDIUM.value: os.getenv('REMINDER_INTERVAL_FOR_MEDIUM', 24),
            TaskCriticality.HIGH.value: os.getenv('REMINDER_INTERVAL_FOR_HIGH', 10),
            TaskCriticality.CRITICAL.value: os.getenv('REMINDER_INTERVAL_FOR_CRITICAL', 5),
        }
        
        self.email_helper = EmailHelper(bot_email=self.BOT_EMAIL)
        
        self.endpoints = {
            'login'         : f'{self.API_BASE_URL}/token/',
            'create_task'   : f'{self.API_BASE_URL}/api/tasks/',
            'update_task'   : f'{self.API_BASE_URL}/api/tasks/%s',
            'thread_exists' : f'{self.API_BASE_URL}/api/tasks/?thread_id=%s',
            'open_tasks'    : f'{self.API_BASE_URL}/api/tasks/?status=OPEN',
            'reminder_sent' : f'{self.API_BASE_URL}/api/tasks/%s/remindersent',
        }
        
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        self.login()
        
    def login(self):
        """Logs in to the API and returns the access token."""
        response = requests.post(self.endpoints['login'], data={'username': self.USER_NAME, 'password': self.PASSWORD})
        response.raise_for_status()  # Raise an exception for HTTP errors

        if 'access_token' not in response.json():
            raise ValueError("Access token not found in login response")
        
        self.token = f'Bearer {response.json()["access_token"]}'
        self.headers['Authorization'] = self.token
        
        return response.json()['access_token']
    
    def create_task(self, creator_name: str, assigner_name: str, subject: str, 
                        criticality: str, status: str, 
                        thread_id: str, html_file_path: str) -> requests.Response:
        """
        Creates a task using the API.

        Args:
            creator_name (str): The name of the task creator.
            assigner_name (str): The name of the task assigner.
            subject (str): The subject of the task.
            criticality (TaskCriticality): The criticality level of the task.
            status (TaskStatus): The status of the task.
            thread_id (str): The thread ID associated with the task.
            html_file_path (str): The file path of the HTML file to be attached to the task.

        Returns:
            requests.Response: The response from the API.

        Raises:
            FileNotFoundError: If the HTML file does not exist.
        """
        with open(html_file_path, 'rb') as html_file:
            files = {'html_file': html_file}
            data = {
                'creator_name': creator_name,
                'assigner_name': assigner_name,
                'subject': subject,
                'criticality': criticality,
                'status': status,
                'thread_id': thread_id,
            }
            self.log.info(data)
            
            create_task_headers = self.headers.copy()
            create_task_headers.pop('Content-Type', None)
            # create_task_headers['Content-Type'] = 'multipart/form-data'
            response = requests.post(self.endpoints['create_task'], headers=create_task_headers, data=data, files=files)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
        self.log.info('Task created successfully!')
        self.log.info(response.json())
        return response

    def update_task(self, task_id: int, html_file_path: str) -> requests.Response:
        """
        Updates a task using the API.

        Args:
            task_id (int): The ID of the task to be updated.
            html_file_path (str): The file path of the HTML file to be attached to the task.

        Returns:
            requests.Response: The response from the API.

        Raises:
            FileNotFoundError: If the HTML file does not exist.
        """
        with open(html_file_path, 'rb') as html_file:
            files = {'html_file': html_file}

            update_task_headers = self.headers.copy()
            update_task_headers.pop('Content-Type', None)
            # update_task_headers['Content-Type'] = 'multipart/form-data'
            response = requests.put(self.endpoints['update_task'] % task_id, headers=update_task_headers, files=files)
            response.raise_for_status()  # Raise an exception for HTTP errors

        self.log.info('Task updated successfully!')
        self.log.info(response.json())
        return response

    def create_task_with_retries(self, creator_name: str, assigner_name: str, subject: str, 
                            criticality: str, status: str, 
                            thread_id: str, html_file_path: str) -> None:
        """
        Handles task creation using the API.

        Args:
            creator_name (str): The name of the task creator.
            assigner_name (str): The name of the task assigner.
            subject (str): The subject of the task.
            criticality (TaskCriticality): The criticality level of the task.
            status (TaskStatus): The status of the task.
            thread_id (str): The thread ID associated with the task.
            html_file_path (str): The file path of the HTML file to be attached to the task.

        Returns:
            None

        Raises:
            requests.RequestException: If an error occurs during the API request.
        """
        retries = 3
        for _ in range(retries):
            try:
                self.create_task(creator_name, assigner_name, subject, criticality, status, thread_id, html_file_path)
                break
            except requests.RequestException as e:
                self.log.info("An error occurred:", e)
                self.log.exception("Failed to create task. Retrying...")
                traceback.print_exc()
                self.login()
        else:
            self.log.info("Failed to create task after", retries, "attempts.")
            
    def check_if_task_exists(self, thread_id: str) -> int:
        """
        Checks if a task with the given thread ID already exists.

        Args:
            thread_id (str): The thread ID to check.

        Returns:
            int: The ID of the task if it exists, 0 otherwise
        """
        response = requests.get(self.endpoints['thread_exists'] % thread_id, headers=self.headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        return response.json()[0]['id'] if response.json() else 0
    
    ## Email Related Functions ##
    
    def process_incoming_emails(self, max_results: int = 1, download_email: bool = True) -> list:
        """
        Fetches and processes incoming emails.

        Args:
            max_results (int): The maximum number of emails to read.
            download_email (bool): Whether to download the email content.

        Returns:
            list: A list of email data.
        """
        self.log.info("Processing incoming emails...")
        emails = self.email_helper.fetch_unread_emails(max_results=max_results, download_email=download_email)
        
        for email in emails:
            self.log.info(email)
            try:
                task_id = self.check_if_task_exists(email['thread_id'])
            
                if task_id:
                    self.log.info("Task already exists. Updating task...")
                    self.update_task(task_id=task_id, html_file_path=email['html_file'])
                else:
                    self.log.info("Task does not exist. Creating task...")
                    to_address = email['to']
                    if self.BOT_EMAIL in to_address:
                        to_address.remove(self.BOT_EMAIL)
                        
                    if not to_address:
                        self.email_helper.send_reply(thread_id=email['thread_id'], reply_text="No assignee found. Skipping task creation.")
                        self.log.info("No assignee found. Skipping task creation. Email:", email['to'])
                        continue
                    self.create_task_with_retries(creator_name=email['from']['email'], assigner_name=to_address[0], 
                                                subject=email['subject'], criticality=TaskCriticality.MEDIUM.value, status=TaskStatus.OPEN.value, 
                                                thread_id=email['thread_id'], html_file_path=email['html_file'])
                    
                os.remove(email['html_file'])
            except Exception as e:
                self.log.error("An error occurred:", e)
                self.log.exception("Failed to process email.")
                traceback.print_exc()

        return emails

    def send_reminders(self):
        """Sends reminders for tasks that are overdue or due soon."""
        # Fetch tasks that are open => check criticality => last reminder sent => if last reminder time > x interval (wrt critcality) => send reminder
        response = requests.get(self.endpoints['open_tasks'], headers=self.headers)
        response.raise_for_status()
        
        for task in response.json():
            task_id = task['id']
            critcality = task['criticality']
            status = task['status']
            thread_id = task['thread_id']
            created_time = task['created_time']
            
            # 2024-07-05 19:53:40.826519
            last_reminder_sent = task['last_reminder_sent_time'] # None if not sent
            self.log.info(f'{task_id}, {critcality}, {status}, {thread_id}, {last_reminder_sent}, {created_time}')
            
            # Check if reminder should be sent
            current_time = datetime.datetime.now()
            temp_time_str : str = last_reminder_sent if last_reminder_sent else created_time
            last_reminder_time = datetime.datetime.strptime(temp_time_str.split('.')[0], "%Y-%m-%dT%H:%M:%S")
            time_diff = current_time - last_reminder_time
            
            if time_diff.total_seconds() < (float(self.REMINDER_INTERVALS[critcality]) * 60 * 60):
                self.log.debug(f'Skipping reminder for task {task_id}. Last reminder sent {time_diff.total_seconds()} seconds ago.')
                continue
            
            # Send reminder
            reply_text = f"""
            <p>This is a reminder for the task. Please check this at your earliest convenience.</p>
            
            <p>Task Criticality: {critcality}</p>
            <p>Task Status: {status}</p>
            
            <p>If the task is completed, please mark it as 'FIXED' or 'CLOSED'.</p>
            <p>Here: <a href="{self.TASK_EDIT_URL % task_id}">{self.TASK_EDIT_URL % task_id}</a></p>
            """
            self.email_helper.send_reply(thread_id=thread_id, reply_text=reply_text.strip())
            
            response = requests.post(self.endpoints['reminder_sent'] % task_id, headers=self.headers)
            response.raise_for_status()
            self.log.info("Reminder sent successfully!")

# task_processor = TaskProcessor()
# task_processor.process_incoming_emails(max_results=10, download_email=True)
# task_processor.send_reminders()



