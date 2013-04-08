from datetime import datetime
from django.db import models
import tasks

class Bill(models.Model):
    CRON_CHOICES = (
            ('', 'Run once', ''),
            ('0 0 1 * *', 'First of every month'),
            ('0 0 * * 0', 'Weekly'),
            )

    name = models.CharField(max_length=30)
    cron = models.CharField(default='',
                            max_length=20,
                            choices=CRON_CHOICES,
                            verbose_name='Repeats')

    def next_run(self):
        if self.cron: #  This bill reoccurs
            now = datetime.now()
            cron = croniter.croniter(self.cron, now)
            return cron.get_next(datetime.datetime)

    def save(self, *args, **kwargs):
        super(Bill, self).save(*args, **kwargs)
        tasks.process_bill.delay(bill_id=self.id)

