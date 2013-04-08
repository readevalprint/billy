from datetime import datetime, timedelta
import sys

from celery import Celery

celery = Celery('tasks', broker='amqp://koflwbpt:H6EPt6dYmHLZegMV4IGWqbILBCHFYhXc@tiger.cloudamqp.com/koflwbpt')

@celery.task(name='process_bill')
def process_bill(bill_id):
    print sys.path
    from models import Bill
    bill = Bill.objects.get(id=bill_id)
    print "Processed bill: {bill_name}".format(bill_name=bill.name)
    eta = bill.next_run()
    if eta:
        process_bill.apply_async(bill_id, eta=eta)

