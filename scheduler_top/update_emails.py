from stock_web.models import Emails
from stock_web.email import send
def send_emails():
    email_list=Emails.objects.filter(sent=False)
    if len(email_list)>0:
        for email in email_list:
            try:
                send(email.subj, email.text, email.to)
                email.sent=True
                email.save()
            except:
                pass
    else:
        pass