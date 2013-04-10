import balanced
from django.contrib.auth.models import User
from django.utils import unittest
from mock import patch

from django_balanced.models import Card
from models import DebitTask, TaskRunner


class DebitTaskTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Bob')
        self.cc = balanced.Card(
            card_number="5105105105105100",
            expiration_month="12",
            expiration_year="2015",
            ).save()
        self.card = Card.create_from_card_uri(self.user, self.cc.uri)

    @patch('balanced_tasks.tasks.process_balanced_task.apply_async')
    def test_save_and_process_bill(self, apply_async):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        apply_async.assert_called_once_with((d.id,), eta=None, task_id=d.runner.task_id)
