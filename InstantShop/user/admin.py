from django.contrib import admin
from .models import CustomerUser, Products, ProductComments, Comment

# Register your models here.
admin.site.register(CustomerUser)
admin.site.register(Products)
admin.site.register(ProductComments)
admin.site.register(Comment)