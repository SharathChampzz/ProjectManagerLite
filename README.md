# Project Manage Lite
ProjectManagerLite is designed to automate the daily task follow-ups of project managers, ensuring that developers receive timely reminders to address issues reported by testers. This microservice-based project includes email service, FTP service, UI service, and web service to streamline task management and communication.

# Design:
![image](https://github.com/user-attachments/assets/268bb686-b82f-449a-8623-5992e67d1b94)

# How It Works?
### Overview
When a tester reports an issue to a developer, they also include the project manager bot's email alias. The email service reads these emails (authentication using a token JSON) and queries the web service to check if a task is already created based on the thread ID. If not, a new task is created; otherwise, the existing task is updated. The email service includes two main components: the listener and the reminder sender.

# Components
### Email Service

* **Mail Listener**:  
Reads emails at regular intervals using APScheduler, checks if a task exists, and creates/updates tasks accordingly.
* **Mail Sender**: 
Sends reminders to developers about open tasks, with intervals based on task criticality. Critical tasks receive more frequent reminders.
Scheduler: Configured to listen to emails every x minutes and send reminders every y minutes.

### Web Service
* Built using FastAPI.
* Performs CRUD operations on tasks.
* Stores file references in the database for future access.
* Uses SQLite for lightweight database management.
* Authentication enabled.

### UI Service
* Built using React.
* Displays all issues and allows CRUD operations from the UI.
* Involves Signup and Login

### FTP Service
* Built using FastAPI.
* Handles HTML file uploads when creating tasks, acts as FTP Server

# How to run?
### Clone the Repository
```git clone https://github.com/SharathChampzz/ProjectManagerLite.git```

### Handle Prerequisites
Create sqlitedb and provide it in docker-compose.
Create FTP Server Upload Location and provide it in docker-compose.
Generate token JSON for Gmail API and place it in the emailservice folder.

### Build and Run the Project
```docker-compose build```
```docker-compose up```

# Conclusion
ProjectManagerLite automates the follow-up tasks of project managers, ensuring developers are consistently reminded about their tasks. It is a comprehensive solution combining email automation, task management, and a user-friendly interface to enhance productivity.
