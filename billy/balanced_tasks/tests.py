import balanced
from django.contrib.auth.models import User
from django.test import TestCase

from mock import patch

from django_balanced.models import Card
from models import DebitTask


class DebitTaskTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Bob')
        self.cc = balanced.Card(
            card_number="5105105105105100",
            expiration_month="12",
            expiration_year="2015").save()
        self.card = Card.create_from_card_uri(self.user, self.cc.uri)

    @patch('balanced_tasks.tasks.process_balanced_task.apply_async')
    def test_create_and_start(self, apply_async):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        # Was it sent to Celery?
        apply_async.assert_called_once_with((d.id,),
                                            eta=None,
                                            task_id=d.runner.task_id)

    def test_stop(self):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        assert d.runner.task_id
        d.stop()
        assert d.runner.task_id == ''

    def test_delete(self):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        d.delete()
        assert d.is_deleted
        assert d.runner.task_id == ''

    def test_restart(self):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        d.stop()
        d.start()
        assert d.runner.task_id

    def test_restart_overrides_existing(self):
        d = DebitTask.objects.create(amount=100, card=self.card)
        d.start()
        original_task_id = d.runner.task_id
        d.start()
        new_task_id = d.runner.task_id
        self.assertNotEqual(new_task_id, original_task_id)
