from django.contrib import admin
from .models import CustomerUser, Products

# Register your models here.
admin.site.register(CustomerUser)
admin.site.register(Products)