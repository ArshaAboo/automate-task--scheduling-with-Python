# automate-task--scheduling-with-Python
Project Setup
Overview
This application is designed to schedule repetitive tasks and automate logging of task results in an SQL database. It allows you to define multiple tasks (such as running Python scripts or fetching web page results) with custom execution frequencies or at specific times. It automatically determines whether each task succeeds or fails based on configurable keywords, logs the outcome in the database, and sends notifications for failures through email or Microsoft Teams (for high-priority tasks). This ensures continuous monitoring, timely alerts, and historical tracking of task executions.

Prerequisites
Python Version: 3.9.13
Required Packages:
Install the following packages via pip:
pip install schedule requests pandas beautifulsoup4 pyodbc
Configuration
Run the program by --> python runTasks.py (Need to run only this.)

Configuration File: config.json
Task Execution
Failure/Success Determination:
The success or failure of tasks is determined by searching for any of the failure_keywords (specified in config.json) within the first 1000 words of the response from the web link.
Script Descriptions
updateDB.py: Contains functions related to database operations, including connecting to the database, inserting entries, and retrieving failed tasks for the current day. emailSend.py: Contains function to send emails with details of failed tasks for the current day. The email body, subject, and other parameters can be modified here. 
postNotification.py: Contains function to post messages to Teams for high-priority tasks. Messages are posted as adaptive cards.

