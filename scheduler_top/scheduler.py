from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from scheduler_top import update_emails, update_stock
import socket


def start():
    # socket prevents double schedulers, can sometimes happen (mainly with dev server)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))
    except socket.error:
        print("!!!scheduler already started, DO NOTHING")
    else:
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_emails.send_emails, "interval", minutes=30, jitter=120)
        scheduler.add_job(update_stock.update_counts, "interval", hours=2, jitter=120)
        scheduler.start()
