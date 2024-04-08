import requests
import json

def send_notification(registration_ids , message_title , message_desc,message_type,image_url):
    fcm_api = "AAAA0VFMIUc:APA91bFMe4mI8B9F96q1pmnSfd-bVcduAPUfmoWs6fPc345SeluUXPwkHw6PEncCAp8A9dUfhaZvUBI7AHWmkwsqOHlko35q3mW75xOxN5NqZVQl-g58dG-2GWPUjb2-4A6gf6TxDA0A"
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api}
    
    print(image_url)
    payload = {
        "registration_ids" :registration_ids,
        "priority" : "high",
        "notification" : {
            "body" : message_desc,
            "title" : message_title,
            "image": image_url
        },
        "android": {
          "imageUri": image_url,
        },
        
        "data": {
            "type": message_type,
            "event_id": "mappla",
            "image_url": image_url
        }
    }

    result = requests.post(url,  data=json.dumps(payload), headers=headers )
    print(result.json())

def send():
    # registration  = ['eI9wVZaaSRyG09SkuoVrp3:APA91bEUk1IxYUKuSKwGVUxQBCJUSUHR6KjsDT6_dL1m6b-o_VsNyo24KNT-pRT3Am9n4faNDn-kTdenlvr6RieCFWVA4BcnfOV36w8JDqU7Xj8vpsVGlKTKX7Rxmrr0LvJV97CNMbZe']
    registration = ['cDVf47xoSK6MFItfe3usFY:APA91bGmmjhirSMuWKDbvcGM4vG7LheWqU1IdMYA4FP2uT6C_yESioCYSbeIAdOH_PbquY6UkrBhAQTI1Qokq-htz_PJ4KuduzWWbU_RounSg4C74NFaKQaHbDuHua9pTgyBrwYaoi7t']
    send_notification(registration , 'TinkerHub' , 'Congratulations The OGS', 'home' , image_url='https://vcecmediavault.blob.core.windows.net/media/forum/announcements/images/the-ogs-tinkerhub.jpeg')
    print('sent')


if __name__ == "__main__":
    send()
