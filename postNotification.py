import requests

def postTeamsMessage(Webhook_url, task_name, task_id, error_msg, link):
    try:
        adaptive_card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.3",
                        "body": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": "Critical Task Failed!"
                            },
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": f'Task Name: {task_name}'
                            },
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": f'Task ID: {task_id}'
                            },
                            {
                                "type": "TextBlock",
                                "text": error_msg,
                                "wrap": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": link,
                                "url": link
                            }
                        ]
                    }
                }
            ]
        }

        response = requests.post(Webhook_url, json=adaptive_card)
        response.raise_for_status()
        print("Message posted successfully to Teams.")

    except requests.exceptions.RequestException as e:
        print(f"Error posting message to Teams: {e}")
        raise




