from celery.task.base import Task
from mock import patch

from utils import CeleryTestCaseBase
from models import Bill
import tasks


class BillTestCase(CeleryTestCaseBase):
    @patch('bill.tasks.add.delay')
    def test_save_and_task_sent(self, delay):
        b = Bill.objects.create(name='test')
        delay.assert_called_with(4, 4)

