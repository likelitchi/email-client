from django.contrib import admin

from .models import EmailAccount, Email

# Register your models here.

admin.site.register(EmailAccount)
admin.site.register(Email)
