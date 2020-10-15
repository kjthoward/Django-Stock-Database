import json
import os
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText
from django.conf import settings
import pdb
if os.path.exists(os.path.join(os.path.dirname(__file__),"email.json")):
    with open(os.path.join(os.path.dirname(__file__),"email.json")) as json_file:
        email_json=json.load(json_file)
        pw=email_json["password"]
        acc=email_json["account"]
    if pw=="" or acc=="":
        EMAIL=False
    else:
        EMAIL=True
else:
    EMAIL=False


def send(sbj,text,to):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    account = acc
    password = pw
    reply_to = "kieran.howard@ouh.nhs.uk"
    server.login(account,password)
    msg = email.mime.multipart.MIMEMultipart()
    msg["From"]="ORGLStock@gmail.com"
    msg["Subject"]=sbj
    msg.add_header('reply-to', reply_to)
    text+="You can visit the site at: <a href='{0}'> {0} </a><br><br>".format(settings.SITE_URL)
    text+="This message was automatically sent on behalf of the Stock Team.<br><br>"
    #pdb.set_trace()
    html='<html><head></head><body>{}If you have any issues please contact <a href="mailto:Kieran.howard@ouh.nhs.uk?subject=Stock%20Database">kieran.howard@ouh.nhs.uk</a> or reply to this message.</p></body></html>'.format(text)
    msg.attach(MIMEText(html, 'html'))
    msg['to']=to
    server.sendmail(msg['from'], msg['to'], msg.as_string())
    server.quit()    
