from backoffice.celery import app as celery_app

celery_app.conf.beat_schedule.update({
    'Ma man': {
        'task': 'base.tasks.print_random_number',
        'schedule': 30.0,
        'args': ("hello",)
    },
})

@celery_app.task
def print_str(string_to_print):
    print(string_to_print)