from datetime import datetime
from django.db import models
import tasks

import croniter


class Bill(models.Model):
    ONCE = ''
    FIRST_OF_MONTH = '0 0 1 * *'
    WEEKLY = '{sec} {min} * * 0'  # Relative to the created

    CRON_CHOICES = (
        (FIRST_OF_MONTH, 'First of every month'),
        (WEEKLY, 'Weekly'),)

    name = models.CharField(max_length=30)
    cron = models.CharField(default=ONCE,
                            blank=True,
                            max_length=20,
                            choices=CRON_CHOICES,
                            verbose_name='Repeats')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def next_run(self):
        if self.cron:  # This bill reoccurs
            now = datetime.now()
            cron = croniter.croniter(self.cron.format(self.created), now)
            return cron.get_next(datetime.datetime)

    def save(self,   *args, **kwargs):
        super(Bill, self).save(*args, **kwargs)
        tasks.process_bill.delay(bill_id=self.id)
