from django.shortcuts import render

# Create your views here.
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(job_defaults=job_defaults, executors=executors)
scheduler.add_jobstore(DjangoJobStore(), 'default')
register_events(scheduler)
scheduler.remove_all_jobs()
scheduler.start()
