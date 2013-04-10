from datetime import datetime
import uuid

from django.db import models
from django.utils.timezone import now

"""
**balanced_tasks** is a Django app that will allow arbitrary Balanced transations
to be logged and executed, repeatedly if needed. See [tasks.py](tasks.html).

# Usage
This assumes that you have installed django_balanced, its requirements,
and that celery is running.

First create a credit card on BalancedPayment.com

    import balanced

    cc = balanced.Card(
        card_number="5105105105105100",
        expiration_month="12",
        expiration_year="2015",
    ).save()

Now create a referrence to it in Django

    user = User.objects.all()[0]
    card = Card.create_from_card_uri(user, cc.uri)

Create a `DebitTask` to charge this card every minute

TODO: This should be smoother

    d = DebitTask.objects.create(amount=100, card=card)
    d.runner.frequency = TaskRunner.EVERY_MIN
    d.runner.save(force_update=True)
    d.start()

Now you can see th history of this DebitTask

    for event in d.audit_feed.auditevent_set.all():
        print("id: %s message: %s timestamp: %s" % (event.id, event.message, event.created_at))

Keep running this to see the debits grow and when you are ready to stop it

    d.stop()

"""

from annoying.fields import AutoOneToOneField
from django_balanced.models import Card
import croniter

import tasks

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^annoying\.fields\.AutoOneToOneField"])


class TaskRunner(models.Model):
    """
    Manages running tasks as specified by the cron notation in the
    `frequency` field. Once a started (with `start()`) a new `task_id` is
    generated for the new task. If any existing tasks were queued, they will
    skipped if their `task_id` no longer reflects the one saved on the
    TaskRunner instance.

    The cron string can contain the following placeholders::

        "{minute} {hour} {day_of_month} {month} {day_of_week}"

    which will be subsituted for the corresponding valued based on the task's
    `created_at` date.
    """

    # TODO: Make this a setting
    ONCE = ''
    FIRST_OF_MONTH = '0 0 1 * *'
    # The same time and day of week
    WEEKLY = '{minute} {hour} * * {day_of_week}'
    HOURLY = '{minute} * * * *'
    EVERY_MIN = '* * * * *'
    EVERY_2_MIN = '*/2 * * * *'

    CRON_CHOICES = (
        (ONCE, 'Once'),
        (FIRST_OF_MONTH, 'First of every month'),
        (WEEKLY, 'Weekly'),
        (HOURLY, 'Hourly'),
        (EVERY_MIN, 'Every Minute'),
        (EVERY_2_MIN, 'Every 2 Minutes'))

    name = models.CharField(max_length=30, blank=True)
    frequency = models.CharField(default=ONCE,
                                 blank=True,
                                 max_length=20,
                                 choices=CRON_CHOICES,)

    task_id = models.CharField(max_length=36, blank=True, default='')
    last_run = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Don't actually removed the data
    #
    # TODO: Add managers to filter based on is_deleted
    is_deleted = models.BooleanField(default=False)

    def next_run(self):
        """
        Determines the next time this task will be run based on the
        `frequency`, `created_at` and `now()`.

        """
        # TODO: Allow a limit of times to run (eg once a month for 3 months)

        if self.frequency:  # This task reoccurs
            c = {}
            c['hour'] = self.created_at.hour
            c['minute'] = self.created_at.minute
            c['day_of_month'] = self.created_at.day
            c['month'] = self.created_at.month
            c['day_of_week'] = self.created_at.isoweekday()

            return croniter.croniter(self.frequency.format(**c),
                                     now()).get_next(datetime)

    def stop(self):
        """
        Removes the task_id, any existing tasks will refuse to run.
        """

        self.task_id = ''
        self.save(force_update=True)

    def delete(self):
        """
        Removes the `task_id` and sets `is_deleted` to true.
        """

        self.is_deleted = True
        self.task_id = ''
        self.save(force_update=True)

    def start(self):
        """
        Set a new `task_id` on this TaskRunner to invalidate any existing tasks
        and schedual a new one.
        """
        if not self.id:
            raise Exception("Save before running.")
        self.task_id = str(uuid.uuid4())
        self.save(force_update=True)
        tasks.process_balanced_task.apply_async((self.id,),
                                                eta=self.next_run(),
                                                task_id=self.task_id)

    def save(self, *args, **kwargs):
        """
        Generally TaskRunners should only be created and not modified. But
        use `force_update` if needed
        """
        if self.pk is None or kwargs.get('force_update', False):
            super(TaskRunner, self).save(*args, **kwargs)
        else:
            raise Exception('Cannot modify existing BalancedTask. Delete '
                            'and create a new one or use force_update=True')


class AuditFeed(models.Model):
    """
    A simple aggregator of AuditEvents.
    """

    def add_event(self, message):
        AuditEvent.objects.create(message=message, feed=self)


class AuditEvent(models.Model):
    """
    Logs what happens to a Task.
    """
    # TODO: Make this more robust, add who is doing what.
    feed = models.ForeignKey(AuditFeed)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class BalancedBaseTask(models.Model):
    """
    Links a TaskRunner to an AuditFeed for running and logging
    reoccuring Balanced tasks.
    Should not be instantiated on its own.

    TODO: Set the `self.runner.frequency` here or in a Form.
    """
    # NOTE: Go back to OneToOne fields?
    runner = AutoOneToOneField(TaskRunner, related_name='balanced_task')
    audit_feed = AutoOneToOneField(AuditFeed,
                                   editable=False,
                                   related_name='balanced_task')

    description = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        is_new = self.id is None
        if is_new:
            # Create the needed `TaskRunner` and `AuditFeed`
            self.runner = TaskRunner.objects.create()
            self.audit_feed = AuditFeed.objects.create()
        super(BalancedBaseTask, self).save(*args, **kwargs)

    def delete(self):
        """
        Don't actually remove data. Just stop the task, an set `is_deleted`.
        """
        self.is_deleted = True
        self.stop()
        self.save(force_update=True)
        self.audit_feed.add_event("Task Deleted")

    # TODO: Let the `Start()`, `stop()` and `run()` functions take and
    # extra reason parameter to add to the message.
    def start(self):
        '''Helper shortcut'''
        self.runner.start()
        self.audit_feed.add_event("Task Started")

    def stop(self):
        '''Helper shortcut'''
        self.runner.stop()
        self.audit_feed.add_event("Task Stopped")

    def run(self):
        '''Override this method in a subclass'''
        raise NotImplementedError()

    def __unicode__(self):
        return self.description


class DebitTask(BalancedBaseTask):
    """
    Charge the `card` an $`amount` according to the `runner.frequency`
    """
    card = models.ForeignKey(Card)
    amount = models.IntegerField(default=0, blank=True)

    def run(self):
        """
        Overrides `run` in the `BalancedBaseTask` superclass.

        Will be called from the celery task in [tasks.py](tasks.html)
        """
        debit = self.card.debit(self.amount, self.description)
        self.audit_feed.add_event("Task Run: $%.2f" % (int(self.amount)/100.0,))

    def __unicode__(self):
        return 'DebitTask: %s' % self.id
