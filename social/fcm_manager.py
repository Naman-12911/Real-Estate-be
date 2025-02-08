import firebase_admin
from firebase_admin import credentials, messaging
from realEstate.settings import FCM_SERVICE_KEY


cred = credentials.Certificate(FCM_SERVICE_KEY)
firebase_admin.initialize_app(cred)


def sendPush(title, msg, registration_token, dataObject=None):
    alert = messaging.ApsAlert(title = title, body = msg)
    aps = messaging.Aps(alert = alert, sound = "default", mutable_content = True)
    
    payload = messaging.APNSPayload(aps)

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title,
                                            body=msg,
                                            ),
        data=dataObject,
        tokens=registration_token,
        apns = messaging.APNSConfig(payload = payload)
    )

    response = messaging.send_multicast(message)
    print('successfully sent message', response)