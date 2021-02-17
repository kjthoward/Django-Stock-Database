from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from email_scheduler import update_emails
import socket
def start():
    #socket prevents double schedulers, can sometimes happen (mainly with dev server)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))
    except socket.error:
        print("!!!scheduler already started, DO NOTHING")
    else:
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_emails.send_emails, 'interval', minutes=30, jitter=120)
        scheduler.start()