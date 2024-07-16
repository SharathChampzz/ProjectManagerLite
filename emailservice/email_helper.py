from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import base64
from email.mime.text import MIMEText
import re

# convert *.eml to *.html
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup

# type hinting
from typing import List, Dict, Any
from datetime import datetime

import logging

# Set execution path to the current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',          # Read-only access to Gmail
    'https://www.googleapis.com/auth/gmail.modify',            # Read and write access to Gmail, excluding permanent deletion of threads and messages
    'https://www.googleapis.com/auth/gmail.compose',           # Send email on your behalf
    'https://www.googleapis.com/auth/gmail.send',              # Send email on your behalf
    'https://www.googleapis.com/auth/gmail.labels',            # Manage your labels
    # 'https://www.googleapis.com/auth/gmail.metadata',          # View your email message metadata such as labels and headers, but not the email body
    'https://www.googleapis.com/auth/gmail.settings.basic',    # Manage your basic mail settings
    'https://www.googleapis.com/auth/gmail.settings.sharing',  # Manage your sensitive mail settings, including who can manage your mail
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose', # Read and write access to the current compose window
    'https://www.googleapis.com/auth/gmail.addons.current.message.action', # Read and write access to the current message
    'https://www.googleapis.com/auth/gmail.addons.current.message.metadata', # View the metadata of the current message
    'https://www.googleapis.com/auth/gmail.addons.current.message.readonly', # Read the current message
]

class EmailHelper():
    """A helper class for interacting with Gmail using the Gmail API."""
    
    def __init__(self, bot_email: str) -> None:
        """Initializes the Gmail service and allowed email domains."""
        self.log = logging.getLogger('app')
        self.creds = self.authenticate_gmail()
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.bot_email = bot_email
        self.allowed_domains = ['gmail.com']
    
    def authenticate_gmail(self) -> Credentials:
        """Authenticates the Gmail service using OAuth2.0."""
        self.log.info('Authenticating Gmail...')
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def mark_as_read(self, message_id: str) -> bool:
        """Marks an email as read."""
        try:
            self.log.info('Marking email as read...')
            self.gmail_service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
            self.log.info(f"Marked message {message_id} as read.")
            return True
        except Exception as error:
            self.log.exception(f"An error occurred while marking the message as read: {error}")
            return False

    def extract_emails(self, text) -> List[str]:
        """Extracts email addresses from the given text."""
        # Regular expression pattern for matching email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Find all matches of the pattern in the input text
        emails = re.findall(email_pattern, text)
        
        return emails

    def get_unread_emails(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetches unread emails from Gmail."""
        query = 'in:inbox is:unread'  # Filter for unread emails in inbox
        results = self.gmail_service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        if not messages:
            self.log.info("No unread messages found.")
            return {}
        self.log.info(f"Found {len(messages)} unread messages.")
        return messages

    def download_email_as_html(self, message_id: str) -> str:
        """Method to download an email as an EML file and convert it to HTML."""
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        eml_file = f'downloads/temp.eml'
        self.download_eml(message_id, eml_file) # download email as eml file
        
        html_file = f'downloads/{message_id}.html'
        self.convert_eml_to_html(eml_file=eml_file, output_file=html_file) # convert eml to html
        
        return html_file

    def fetch_unread_emails(self, download_email: bool = False, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches unread emails from Gmail.

        Args:
            download_email: Whether to download the email as an EML file and convert it to HTML.
            max_results: The maximum number of results to fetch.

        Returns:
            A dictionary containing the details of the fetched email.
        """
        # TODO: Break down the function into smaller functions for better readability and maintainability
        messages = self.get_unread_emails(max_results)
        
        filtered_messages = []
        checked_threads = []
        
        for message in messages:
            try:
                msg = self.gmail_service.users().messages().get(userId='me', id=message['id']).execute()
                # self.log.info(f"Message snippet: {msg['snippet']}")

                message_id = msg['id']
                thread_id = msg['threadId']
                content = msg['snippet']
                
                # Code to handle mutliple messages in the same thread, skip if already checked.
                # We always get the latest message in the first iteration and we need only that.
                if thread_id in checked_threads:
                    self.log.info(f"Thread {thread_id} already checked. Skipping and marking this message as read...")
                    self.mark_as_read(message_id)
                    continue
                checked_threads.append(thread_id)
                
                headers = msg['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "")
                from_address = self.extract_emails(next((header['value'] for header in headers if header['name'] == 'From'), ""))[0]
                to_address = self.extract_emails(next((header['value'] for header in headers if header['name'] == 'To'), ""))
                cc_address = self.extract_emails(next((header['value'] for header in headers if header['name'] == 'Cc'), ""))
                self.log.info(f'Subject: {subject}\nFrom: {from_address}\nTo: {to_address}\nCC: {cc_address}\nMessage ID: {message_id}\nThread ID: {thread_id}')


                # # Extract name and email from the from_address
                # parts = from_address.split("<")
                # sender_name, sender_email = parts[0].strip().strip('"'), parts[1].strip()[:-1]
                # self.log.info(f'Sender Name: {sender_name}, Sender Email: {sender_email}')

                # Mark the message as read
                self.mark_as_read(message_id)

                if from_address.split('@')[1] not in self.allowed_domains:
                    self.log.info(f"Sender email domain {from_address.split('@')[1]} not allowed.")
                    continue

                if download_email:
                    html_file = self.download_email_as_html(message_id)

                filtered_messages.append({
                    "message_id": message_id,
                    "thread_id": thread_id,
                    "subject": subject,
                    "from": {
                        "name": "",
                        "email": from_address
                    },
                    "to": to_address,
                    "cc": cc_address,
                    "content": content,
                    "html_file": html_file if download_email else ""
                })
                self.log.info('')
            except ValueError as error:
                self.log.exception(f"An error occurred while fetching email: {error}")
            
        return filtered_messages
            
    def download_eml(self, message_id: str, output_file: str) -> str:
        """Downloads an email as an EML file."""
        self.log.info(f"Downloading email with ID: {message_id}...")
        msg = self.gmail_service.users().messages().get(userId='me', id=message_id, format='raw').execute()
        raw_data = msg['raw']
        byte_data = base64.urlsafe_b64decode(raw_data.encode('UTF-8'))
        
        with open(output_file, 'wb') as f:
            f.write(byte_data)
            
        self.log.info(f"Downloaded email as {output_file}")
        
        return output_file
        
    def convert_eml_to_html(self, eml_file: str, output_file: str) -> str:
        """Convert an EML file to HTML."""
        self.log.info(f"Converting {eml_file} to HTML...")
        with open(eml_file, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        html_content = ""
        image_cid_map = {}

        # Iterate through email parts
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/html':
                html_content = part.get_payload(decode=True).decode('utf-8')
            elif part.get('Content-ID'):
                cid = part['Content-ID'][1:-1]  # Remove <> around CID
                image_data = part.get_payload(decode=True)
                image_type = part.get_content_type().split('/')[1]
                base64_image = base64.b64encode(image_data).decode('utf-8')
                image_cid_map[cid] = f"data:image/{image_type};base64,{base64_image}"

        # Embed images in HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src.startswith('cid:'):
                cid = src[4:]
                if cid in image_cid_map:
                    img['src'] = image_cid_map[cid]

        # Write the modified HTML content to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
            
        self.log.info(f"Converted {eml_file} to HTML as {output_file}")
        
        return output_file

    def __create_reply_message(self, messages, reply_text):
        """Creates a reply message based on the original message and reply text."""
        # pick the last message in the thread where the bot is not the sender
        self.log.info(f'Number of messages in the thread: {len(messages)}')
        original_message = self.__get_original_message(messages)

        headers = original_message['payload']['headers']
        to, cc, subject, message_id, from_addr = self.__extract_message_details(headers)

        if not subject.startswith('Re:'):
            subject = 'Re: ' + subject

        reply_all_to_addresses = self.__get_reply_all_addresses(from_addr, to, cc)

        reply_message = MIMEMultipart()
        reply_message['to'] = ', '.join(reply_all_to_addresses)
        reply_message['cc'] = ', '.join(cc) if cc else ''
        reply_message['from'] = 'me'
        reply_message['subject'] = subject
        reply_message['In-Reply-To'] = message_id
        reply_message['References'] = message_id

        reply_html = self.__create_reply_html(reply_text)
        reply_message.attach(MIMEText(reply_html, 'html'))

        raw = base64.urlsafe_b64encode(reply_message.as_bytes()).decode('utf-8')
        return {'raw': raw, 'threadId': original_message['threadId']}

    def __get_original_message(self, messages):
        """Returns the original message in the thread where the bot is not the sender."""
        original_message = messages[-1]  # default to the last message in the thread
        for message in reversed(messages):
            message_found = False
            for header in message['payload']['headers']:
                if header['name'] == 'From' and self.bot_email not in header['value']:
                    self.log.info('Found a message where the bot is not the sender.')
                    original_message = message
                    message_found = True
            if message_found:
                break
        else:
            self.log.info("No message found where the bot is not the sender.")
        return original_message

    def __extract_message_details(self, headers):
        """Extracts the relevant details from the message headers."""
        to = []
        cc = []
        subject = None
        message_id = None
        from_addr = None

        for header in headers:
            if header['name'] == 'To':
                to.extend(self.extract_emails(header['value']))
            elif header['name'] == 'From':
                from_addr = self.extract_emails(header['value'])[0]
            elif header['name'] == 'Cc':
                cc.extend(self.extract_emails(header['value']))
            elif header['name'] == 'Subject' or header['name'] == 'subject':
                subject = header['value']
            elif header['name'] == 'Message-ID':
                message_id = header['value']

        return to, cc, subject, message_id, from_addr

    def __get_reply_all_addresses(self, from_addr, to, cc):
        """Returns the list of reply all addresses, excluding the bot's email."""
        reply_all_to_addresses = to + [from_addr]  # include the sender in the reply all

        if self.bot_email in reply_all_to_addresses:
            reply_all_to_addresses.remove(self.bot_email)
        if self.bot_email in cc:
            cc.remove(self.bot_email)

        if not reply_all_to_addresses:
            reply_all_to_addresses = cc.copy()  # if no 'To' addresses, use 'Cc' addresses
            cc = []  # clear 'Cc' addresses

        return reply_all_to_addresses

    def __create_reply_html(self, reply_text):
        """Creates the HTML content for the reply message."""
        reply_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        background-color: #F5F5F5;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        line-height: 1.5;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        background-color: #afbacc;
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        margin: 20px;
                        padding: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    {reply_text}
                </div>
            </body>
        </html>
        """
        return reply_html

    def send_reply(self, thread_id, reply_text):
        """Sends a reply to the latest message in a thread."""
        messages = self.gmail_service.users().threads().get(userId='me', id=thread_id).execute().get('messages', [])
        if not messages:
            self.log.info("No messages found in the thread.")
            return None

        reply_message = self.__create_reply_message(messages, reply_text)
        sent_message = self.gmail_service.users().messages().send(userId='me', body=reply_message).execute()
        self.log.info(f"Reply sent: {sent_message['id']}")
        return sent_message

# # Usage example
email_helper = EmailHelper(bot_email='spammingescape@gmail.com')
# # emails = email_helper.fetch_unread_emails(download_email=True, max_results=1)
# # self.log.info(emails)


# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# reply_text = f"Thank you for your email. I will get back to you shortly. Click: http://localhost:3000/tasks/1. Next reply at: {current_time}"
# email_helper.send_reply('190833d498493f68', reply_text)
