import logging

from celery import task
from django.utils.timezone import now

logger = logging.getLogger(__name__)


@task(name='process_task', ignore_result=True)
def process_balanced_task(task_runner_id):
    from models import TaskRunner
    task_runner = TaskRunner.objects.get(id=task_runner_id)

    if (task_runner.task_id != process_balanced_task.request.id
            or task_runner.is_deleted):
        raise Exception("No longer a valid task")

    # The good part
    task_runner.balanced_task.run()
    task_runner.last_run = now()
    task_runner.save(force_update=True)
    eta = task_runner.next_run()

    logger.info('Processed TaskRunner: {bt}'
                ' id: {id} eta:{eta}'.format(
                bt=task_runner.name,
                id=task_runner.id,
                eta=eta))
    if eta:
        task_runner.start()
