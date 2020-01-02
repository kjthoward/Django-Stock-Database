import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

if os.path.exists(os.path.join(os.path.dirname(__file__),"email.json")):
    with open(os.path.join(os.path.dirname(__file__),"email.json")) as json_file:
        email_json=json.load(json_file)
        pw=email_json["password"]
    if pw=="":
        EMAIL=False
    else:
        EMAIL=True
else:
    EMAIL=False


def send(sbj,text,to):
    sg=SendGridAPIClient(pw)
    
    text+="You can visit the site at: {}<br><br>".format(settings.SITE_URL)
    text+="This message was automatically sent on behalf of the Stock Team<br><br>"
    html='<html><head></head><body>{}If you have any issues please contact <a href="mailto:Kieran.howard@ouh.nhs.uk?subject=Stock%20Database">kieran.howard@ouh.nhs.uk</a> or reply to this message</p></body></html>'.format(text)
    message=Mail(                 
                 from_email="ORGLStock@gmail.com",
                 subject=sbj,
                 to_emails=to,
                 html_content=html)
    message.reply_to = "kieran.howard@ouh.nhs.uk"
    return sg.send(message)
