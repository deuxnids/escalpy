import os
from apscheduler.schedulers.blocking import BlockingScheduler
from escalpy.escalpy import Escalpy

sched = BlockingScheduler()



@sched.scheduled_job('interval', seconds=3)
def timed_slf():
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
    escalpy.load_from_firebase(config, user, pw)
    escalpy.assign_avalanche()
    escalpy.save_to_firebase(config, user, pw)
    print os.environ["mailchimp-key"]
    print('This job is run every three minutes.')


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
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
    escalpy.send_emails()

sched.start()
