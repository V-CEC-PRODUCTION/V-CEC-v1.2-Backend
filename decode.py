import requests
import json

def send_notification(registration_ids , message_title , message_desc):
    fcm_api = "AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3"
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
    registration  = ['eF5_gLolTPeWKeIERkJCpo:APA91bFHa8h6e5Li89FGT0SICYv5gHumjSUouCpT1G56epiPbBuuPm9KquFuNfyDHQAbgPAeCJMeD815jFbKFNuwP9Kt5U5gfcFYFds7xIVQM8qSxptDZNKioVf0dez3aWGhpUHClHMI']
    send_notification(registration , 'Hello alvin ikka' , 'I love you so much')
    print('sent')


if __name__ == "__main__":
    send()