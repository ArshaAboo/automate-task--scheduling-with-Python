from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def send_failed_tasks_email(email_settings, failed_tasks_grouped):
    try:
        if not failed_tasks_grouped:
            print("No failed tasks for today.")
            return

        try:
            smtp = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
            smtp.ehlo()
            smtp.starttls()
        except (smtplib.SMTPConnectError, smtplib.SMTPException) as e:
            print(f"Error connecting to SMTP server: {e}")
            raise

        subject = "Failed Tasks Summary Report"
        body = "Summary of failed tasks for today:\n\n"
        for task in failed_tasks_grouped:
            try:
                task_id, task_name, error, url, error_count, min_time, max_time = task
                body += f"The following task failed {error_count} times between {min_time} and {max_time}.\n"
                body += f"Task ID: {task_id}\n"
                body += f"Task Name: {task_name}\n"
                body += f"Error: {error}\n"
                body += f"URL: {url}\n"
                body += "-----------------------------\n"
            except ValueError as e:
                print(f"Error processing task data: {e}")
                continue

        msg = MIMEMultipart()
        msg['From'] = email_settings['from']
        msg['To'] = email_settings['to']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            smtp.sendmail(email_settings['from'], [email_settings['to']], msg.as_string())
            print("Failed tasks summary email sent successfully.")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}")
            raise
        finally:
            smtp.quit()
    except Exception as e:
        print(f"An error occurred in send_failed_tasks_email: {e}")
