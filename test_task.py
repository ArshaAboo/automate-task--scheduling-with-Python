import requests
from bs4 import BeautifulSoup
import subprocess

failure_keywords = ['restricted', 'failed', 'timeout', 'error']

def check_for_keywords(text):
    text = text[:1000] if len(text) > 1000 else text
   
    if any(keyword in text.lower() for keyword in failure_keywords):
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

def perform_task(url):
    try:
        
        if not url.startswith("http"):
            script_path = url
            print("Running script")
            output = subprocess.run(['python', script_path], 
            capture_output=True, 
            text=True)
            output = output.stdout
            status, error, result = check_for_keywords(output)

        else:
            print("Running task")
            response = requests.get(url) 
        
            if response.status_code == 200:
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text(separator=' ').strip()
                page_text_clean = '\n'.join([line.strip() for line in page_text.splitlines() if line.strip()])
                status, error, result = check_for_keywords(page_text_clean)
                        
            else:
                error = f"Failed to retrieve data. Status code: {response.status_code}"
                result = None
                status ='F'
    except requests.exceptions.RequestException as e:
        error = f"Request failed for {url}: {e}"
        result = None
        status = 'F'
    return status, result, error

status, result, error = perform_task("E:\scheduled task scripts\KeyJotForm.py")
print("Status:", status)
print("Result:", result)
print("Error:", error)
