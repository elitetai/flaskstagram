from app import app
import requests

def send_email(receiver, image, amount):
    return  requests.post(
        f"https://api.mailgun.net/v3/{app.config.get('MAIL_DOMAIN')}/messages",
        auth=("api", app.config.get('MAIL_KEY')),
        data={"from": "Excited Sender <mailgun@sandbox1279b0990c474ba7a0430b7311bcdaac.mailgun.org>",  
            "to": [receiver.email],
            "subject": f"Thank you for your donation, {receiver.username}!",
            "html": {"<html><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
                f"<div style='text-align:center'><p>Dear {receiver.username}, thank you for the purchase! Here is your photo!</p>"
                    f"<img src='{image.full_image_url}'/>"
                    f"<p>You have paid <strong>RM{amount}</strong> for it!</p></div></html>"
            }})
