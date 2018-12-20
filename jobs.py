import os
from apscheduler.schedulers.blocking import BlockingScheduler
from escalpy.escalpy import Escalpy, start_logging

sched = BlockingScheduler()

start_logging()


@sched.scheduled_job('cron', minute=30)
def conditions():
    config = {
        "apiKey": os.environ["apiKey"],
        "authDomain": os.environ["authDomain"],
        "databaseURL": os.environ["databaseURL"],
        "projectId": os.environ["projectId"],
        "storageBucket": os.environ["storageBucket"],
        "messagingSenderId": os.environ["messagingSenderId"]
    }

    user = os.environ["user"]
    pw = os.environ["pw"]

    key = os.environ["mailchimp-key"]
    usr = os.environ["mailchimp-usr"]
    mailchimp_data = {"key": key, "usr": usr}

    escalpy = Escalpy(mailchimp=mailchimp_data)
    escalpy.update_conditions(config=config, user=user, pw=pw)


@sched.scheduled_job('cron',  minute=30)
def scheduled_job():
    config = {
        "apiKey": os.environ["apiKey"],
        "authDomain": os.environ["authDomain"],
        "databaseURL": os.environ["databaseURL"],
        "projectId": os.environ["projectId"],
        "storageBucket": os.environ["storageBucket"],
        "messagingSenderId": os.environ["messagingSenderId"]
    }

    user = os.environ["user"]
    pw = os.environ["pw"]

    key = os.environ["mailchimp-key"]
    usr = os.environ["mailchimp-usr"]
    mailchimp_data = {"key": key, "usr": usr}

    escalpy = Escalpy(mailchimp=mailchimp_data)
    escalpy.load_from_firebase(config, user=user, pw=pw)
    escalpy.send_emails()


sched.start()
