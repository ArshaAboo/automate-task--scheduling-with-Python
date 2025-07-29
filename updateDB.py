import pyodbc
import datetime
import json

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: The config file was not found.")
    exit()

try:
    db_settings = config["db_connection"]
    table_name = config["table"]
except KeyError as e:
    print(f"Error: Missing key {e} in 'config.json'.")
    exit()

def get_db_connection():
    try:
        connection = pyodbc.connect(
            f"DRIVER={{{db_settings['driver']}}};"
            f"SERVER={db_settings['server']};"
            f"DATABASE={db_settings['database']};"
            f"UID={db_settings['username']};"
            f"PWD={db_settings['password']};"  
        )
        return connection
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        exit()

def insert_to_db(task_id, task_name, task_frequency, run_date, status, result, error, elapsed_time, url):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = f"""
            INSERT INTO {table_name} (TaskID, TaskName, TaskFrequency, RunDate, Status, Result, Error, ExecutionTime, URL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, task_id, task_name, task_frequency, run_date, status, result, error, elapsed_time, url)
        conn.commit()
    except pyodbc.Error as e:
        print(f"Error executing INSERT query: {e}")
    finally:
        cursor.close()
        conn.close()

def get_failed_tasks_today_grouped():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        query = f"""
            SELECT 
                TaskID, 
                TaskName, 
                CAST(Error AS NVARCHAR(MAX)) AS Error,  
                URL, 
                COUNT(*) AS ErrorCount, 
                FORMAT(MIN(CAST(RunDate AS DATETIME)), 'HH:mm:ss') AS MinTime, 
                FORMAT(MAX(CAST(RunDate AS DATETIME)), 'HH:mm:ss') AS MaxTime
            FROM {table_name}
            WHERE Status = 'F' AND CAST(RunDate AS DATE) = ?
            GROUP BY TaskID, TaskName, CAST(Error AS NVARCHAR(MAX)), URL
            ORDER BY TaskID, CAST(Error AS NVARCHAR(MAX))
        """

        cursor.execute(query, today)
        failed_tasks = cursor.fetchall()
        return failed_tasks
    except pyodbc.Error as e:
        print(f"Error executing SELECT query: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        
