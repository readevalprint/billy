from django.contrib import admin
from django import forms

from models import DebitTask


class DebitTaskAdminForm(forms.ModelForm):
    class Meta:
        model = DebitTask


class DebitTaskAdmin(admin.ModelAdmin):
        form = DebitTaskAdminForm


admin.site.register(DebitTask, DebitTaskAdmin)
