import pyfcm

def send_noti():
    push_service = pyfcm.FCMNotification(api_key="AAAA0VFMIUc:APA91bFMe4mI8B9F96q1pmnSfd-bVcduAPUfmoWs6fPc345SeluUXPwkHw6PEncCAp8A9dUfhaZvUBI7AHWmkwsqOHlko35q3mW75xOxN5NqZVQl-g58dG-2GWPUjb2-4A6gf6TxDA0A")
    
    registration = ['cDVf47xoSK6MFItfe3usFY:APA91bGmmjhirSMuWKDbvcGM4vG7LheWqU1IdMYA4FP2uT6C_yESioCYSbeIAdOH_PbquY6UkrBhAQTI1Qokq-htz_PJ4KuduzWWbU_RounSg4C74NFaKQaHbDuHua9pTgyBrwYaoi7t']
    
    message_title = "TinkerHub"
    
    message_body = "Congratulations The OGS"
    
    image_url = "https://vcecmediavault.blob.core.windows.net/media/forum/announcements/images/the-ogs-tinkerhub.jpeg"
    
    extra_notification_kwargs = {
    'image':  image_url
    }
    
    result = push_service.notify_multiple_devices(registration_ids=registration, message_title=message_title, message_body=message_body, data_message={"type": "home", "event_id": "mappla"}, extra_notification_kwargs=extra_notification_kwargs, sound="default")
    
    print(result)
    
if __name__ == "__main__":
    send_noti()