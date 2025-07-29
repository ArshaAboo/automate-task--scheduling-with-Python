import schedule 
import time
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
import pyodbc
import subprocess
import json
from postNotification import postTeamsMessage
from emailSend import send_failed_tasks_email
from updateDB import get_db_connection, insert_to_db, get_failed_tasks_today_grouped

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: The config file was not found.")
    exit()

#Function to determine success or failure of tasks.
def check_for_keywords(text):
    text = text[:1000] if len(text) > 1000 else text
   
    if any(keyword in text.lower() for keyword in config["failure_keywords"]):
        print(f"Failure keyword found.")
        status = 'F'
        error = text
        result = None
    else:
        print(f"No failure keywords found.")
        status ='S'
        error = 'No error'
        result = text
        
    return status, error, result

def perform_task(task_id, task_name, task_frequency, url, priority):
    try:
        print("Running", task_name)
        elapsed_time = 0

        # Check if the URL is actually a script path
        if not url.startswith("http"):
            script_path = url
            print("Running script")
            start_time = time.time()
            # Run the script and capture the output
            output = subprocess.run(['python', script_path], 
            capture_output=True, 
            text=True)
            elapsed_time = round(time.time() - start_time,2)
            output = output.stdout
            # Check the output for failure keywords
            status, error, result = check_for_keywords(output)

        else:
            # Make a GET request to the URL
            response = requests.get(url) 
            if response.status_code == 200:

                elapsed_time =  round(response.elapsed.total_seconds(), 2)

                try:
                    # Parse the HTML content using BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text(separator=' ').strip()
                    page_text_clean = '\n'.join([line.strip() for line in page_text.splitlines() if line.strip()])
                except Exception as e:
                    print(f"An error occurred in parsing: {e}")
                    page_text_clean = ""
                # Check the cleaned text for failure keywords
                status, error, result = check_for_keywords(page_text_clean)
                        
            else:
                error = f"Failed to retrieve data. Status code: {response.status_code}"
                result = None
                status ='F'
    except requests.exceptions.RequestException as e:
        error = f"Request failed for {url}: {e}"
        result = None
        status = 'F'
            
    run_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Insert the task details into the database
    insert_to_db(task_id, task_name, task_frequency, run_date, status, result, error, elapsed_time, url)

    # Send an MS Teams notification if a high priority task fails
    if priority == 'high' and status == 'F':
        print("High priority task failed! Task ID: ", task_id)
        postTeamsMessage(config["webhook_url"], task_name, task_id, error, url)

def schedule_task(row):
    if row['Task_ScheduleType'] == 'frequency':  
        schedule.every(int(row['Task_Frequency/Task_Time'])).seconds.do(perform_task, task_id=row['Task_ID'], task_name=row['Task_Name'], task_frequency=row['Task_Frequency/Task_Time'], url=row['URL'], priority=row['Task_Priority'])
      
    elif row['Task_ScheduleType'] == 'specific_time': 
        schedule.every().day.at(row['Task_Frequency/Task_Time']).do(perform_task, task_id=row['Task_ID'], task_name=row['Task_Name'], task_frequency=row['Task_Frequency/Task_Time'], url=row['URL'], priority=row['Task_Priority'])
       
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

try:
    tasks_df = pd.read_csv(config["tasks_csv_path"])
except FileNotFoundError:
    print(f"File not found: {config['tasks_csv_path']}")
    exit()    

tasks_df.apply(schedule_task, axis=1)
# Schedule email to be sent daily at 5 PM for failed tasks
schedule.every().day.at("17:00").do(lambda: send_failed_tasks_email(config["email_settings"], get_failed_tasks_today_grouped()))

try:
    print("Running tasks!")
    run_scheduled_tasks()
except KeyboardInterrupt:
    print("Program stopped!")














