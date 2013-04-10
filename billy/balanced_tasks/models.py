from datetime import datetime
import uuid

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now

from annoying.fields import AutoOneToOneField
from django_balanced.models import Card
import croniter

import tasks

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^annoying\.fields\.AutoOneToOneField"])


class TaskRunner(models.Model):

    # TODO: Make this a setting
    ONCE = ''
    FIRST_OF_MONTH = '0 0 1 * *'
    WEEKLY = '{minute} {hour} * * {day_of_week}'  # Relative to the created
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
                            choices=CRON_CHOICES,
                            )

    task_id = models.CharField(max_length=36, blank=True, default='')
    last_run = models.DateTimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def next_run(self):
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
        self.task_id = ''
        self.save(force_update=True)

    def delete(self):
        self.is_deleted = True
        self.task_id = ''
        self.save(force_update=True)

    def start(self):
        if not self.id:
            raise Exception("Save before running.")
        self.task_id = str(uuid.uuid4())
        self.save(force_update=True)
        tasks.process_balanced_task.apply_async((self.id,),
                                               eta=self.next_run(),
                                               task_id=self.task_id)

    def save(self, *args, **kwargs):
        if self.pk is None or kwargs.get('force_update', False):
            super(TaskRunner, self).save(*args, **kwargs)
        else:
            raise Exception('Cannot modify existing BalancedTask. Delete '
                            'and create a new one or use force_update=True')


class AuditFeed(models.Model):
    def add_event(self, message):
        AuditEvent.objects.create(message=message, feed=self)



class AuditEvent(models.Model):
    feed = models.ForeignKey(AuditFeed)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class BalancedBaseTask(models.Model):
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
            self.runner = TaskRunner.objects.create()
            self.audit_feed = AuditFeed.objects.create()
        super(BalancedBaseTask, self).save(*args, **kwargs)

    def delete(self):
        self.is_deleted = True
        self.stop()
        self.save(force_update=True)
        self.audit_feed.add_event("Task Deleted")

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
    card = models.ForeignKey(Card)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def run(self):
        tr = self.runner
        frequency = tr.get_frequency_display()
        debit = self.card.debit(self.amount, self.description)
        self.audit_feed.add_event("Task Run: $%s" % (self.amount/100.0,))

    def __unicode__(self):
        return 'DebitTask: %s' % self.id


