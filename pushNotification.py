from pyfcm import FCMNotification
 
push_service = FCMNotification(api_key="AAAAqbxPQ_Q:APA91bGWil8YXU8Zr1CLa-tqObZ-DVJUqq0CrN0O76bltTApN51we3kOqrA4rRFZUXauBDtkcR3nWCQ60UPWuroRZpJxuCBhgD6CdHAnjqh8V2zPIzLvuvERmbipMHIoJJxuBegJW3a3")

registration_ids = ["fvMyZmrbRwKbjA_IGqMMXn:APA91bHsDYoVnK-isJ4N9aaWletaNK_TwyyRq3yWSxvg-HqWb2hrv35FIsWBCJmJkHRoO-v_byjLNQneWr95XUDpgF2ExFJMcCWyPc-5wm9ZIv5fV_D-dQYTvYFZnSL8nFPjBFXdXX4e"]
message_title = 'Hello alvin ikka' 
message_body = 'I love you so much'
result=push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
 
print (result)