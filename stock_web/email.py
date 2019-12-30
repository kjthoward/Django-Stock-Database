import json
import os
import smtplib
import email.mime.multipart
from email.mime.text import MIMEText

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
    reply_to = ""
    server.login(account,password)
    msg = email.mime.multipart.MIMEMultipart()
    msg["From"]=account
    msg["Subject"]=sbj
    msg.add_header('reply-to', reply_to)
    msg.attach(MIMEText(text, "plain"))
    msg['to']=to
    server.sendmail(msg['from'], msg['to'], msg.as_string())
    server.quit()    
