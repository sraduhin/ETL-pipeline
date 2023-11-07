from config.celery import app

from django.core.management import call_command


@app.task
def run_pipeline_task():
    call_command("runpipeline")
