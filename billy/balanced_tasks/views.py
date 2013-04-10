from django.shortcuts import render
from balanced_tasks.models import DebitTask


def home(request):
    tasks = DebitTask.objects.all()
    return render(request, 'index.html', {'tasks': tasks})
