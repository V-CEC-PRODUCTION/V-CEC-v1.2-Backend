from pyfcm import FCMNotification
 
push_service = FCMNotification(api_key="AAAA0VFMIUc:APA91bFMe4mI8B9F96q1pmnSfd-bVcduAPUfmoWs6fPc345SeluUXPwkHw6PEncCAp8A9dUfhaZvUBI7AHWmkwsqOHlko35q3mW75xOxN5NqZVQl-g58dG-2GWPUjb2-4A6gf6TxDA0A")
 
# registration_id = "72651781ed1e567f"
# message_title = "Title"
# message_body = "Hello"
# result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
 
# print (result)
 
# Send to multiple devices by passing a list of ids.
registration_ids = ["72651781ed1e567f"]
message_title = "Title multiple"
message_body = "Hello world!"
result=push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
 
print (result)