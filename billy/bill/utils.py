from django.utils import unittest

from django.test import TestCase
from celery.task.base import Task

from django.test import TestCase
from celery.task.base import Task
import ipdb

class CeleryTestCaseBase(TestCase):

    def setUp(self):
        super(CeleryTestCaseBase, self).setUp()
        self.applied_tasks = []

        self.task_apply_async_orig = Task.apply_async

        @classmethod
        def new_apply_async(task_class, args=None, kwargs=None, **options):
            self.handle_apply_async(task_class, args, kwargs, **options)

        # monkey patch the regular apply_sync with our method
        Task.apply_async = new_apply_async

    def tearDown(self):
        super(CeleryTestCaseBase, self).tearDown()

        # Reset the monkey patch to the original method
        Task.apply_async = self.task_apply_async_orig

    def handle_apply_async(self, task_class, args=None, kwargs=None, **options):
        ipdb.set_trace()
        self.applied_tasks.append((task_class, tuple(args), kwargs))

    def assert_task_sent(self, task_class, *args, **kwargs):
        was_sent = any(task_class == task[0] and args == task[1] and kwargs == task[2]
                       for task in self.applied_tasks)
        self.assertTrue(was_sent, 'Task not called w/class %s and args %s' % (task_class, args))

    def assert_task_not_sent(self, task_class):
        was_sent = any(task_class == task[0] for task in self.applied_tasks)
        self.assertFalse(was_sent, 'Task was not expected to be called, but was. '
                         ' Applied tasks: %s' %                 self.applied_tasks)
