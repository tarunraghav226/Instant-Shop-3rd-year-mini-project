from django.contrib import admin
from .models import CustomerUser, Products, ProductComments, Comment, Cart, Chat, ChatRoom

# Register your models here.
admin.site.register(CustomerUser)
admin.site.register(Products)
admin.site.register(ProductComments)
admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(Chat)
admin.site.register(ChatRoom)