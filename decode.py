# from pyfcm import FCMNotification

# # Your FCM server key obtained from the Firebase Console
# api_key = "AAAA0VFMIUc:APA91bFMe4mI8B9F96q1pmnSfd-bVcduAPUfmoWs6fPc345SeluUXPwkHw6PEncCAp8A9dUfhaZvUBI7AHWmkwsqOHlko35q3mW75xOxN5NqZVQl-g58dG-2GWPUjb2-4A6gf6TxDA0A"

# # Initialize the FCM client
# push_service = FCMNotification(api_key=api_key)

# # The device token obtained from the Flutter app
# device_token = "UE1A.230829.030"

# # The notification message
# message_title = "Your Notification Title"
# message_body = "Your Notification Body"

# # Send the notification
# result = push_service.notify_single_device(
#     registration_id=device_token,
#     message_title=message_title,
#     message_body=message_body
# )

# print(result)
import requests
import json

def send_notification(registration_ids , message_title , message_desc):
    fcm_api = "AAAA0VFMIUc:APA91bFMe4mI8B9F96q1pmnSfd-bVcduAPUfmoWs6fPc345SeluUXPwkHw6PEncCAp8A9dUfhaZvUBI7AHWmkwsqOHlko35q3mW75xOxN5NqZVQl-g58dG-2GWPUjb2-4A6gf6TxDA0A"
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api}

    payload = {
        "registration_ids" :registration_ids,
        "priority" : "high",
        "notification" : {
            "body" : message_desc,
            "title" : message_title,
        }
    }

    result = requests.post(url,  data=json.dumps(payload), headers=headers )
    print(result.json())

def send():
    registration  = ['ebrlDETpQNyVusBXcDIJg1:APA91bHymIhvg-3xnXTWQWFvzTPm_7-Qc0gQjkZZUzGWqq_ua6Qsb-Rs65Ja6k2J0E_IwkhxfryW4AA2vUcQpH8j2r7vFJFbGdr0SAbO-oyAzaB1kSMAvarAJvk3rYc7-dVU7nl9hfqj']
    send_notification(registration , 'Hello alvin ikka' , 'I love you so much')
    print('sent')


if __name__ == "__main__":
    send()