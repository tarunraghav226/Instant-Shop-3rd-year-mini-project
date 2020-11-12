from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.

def user_directory(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.username,filename)


class CustomerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    dob = models.DateField()
    phone_number = models.TextField(max_length=13)
    photo = models.ImageField(upload_to = user_directory, default='default-user-image.png')
    is_email_verified = models.BooleanField(default=False) 
    token = models.CharField(max_length = 30, primary_key = True)

    def __str__(self):
        return str(self.user.username)


class Products(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 40)
    description = models.TextField()
    price = models.DecimalField(max_digits = 100, decimal_places = 3) 
    product_uploaded_on_date = models.DateField()
    selled = models.BooleanField(default=False)
    features = models.TextField()
    months_of_product_used = models.IntegerField()

    img1 = models.ImageField(upload_to = user_directory ,blank=True)
    img2 = models.ImageField(upload_to = user_directory ,blank=True)
    img3 = models.ImageField(upload_to = user_directory ,blank=True)
    img4 = models.ImageField(upload_to = user_directory ,blank=True)

    def __str__(self):
        return self.name+" "+self.user.username


class Comment(models.Model):
    comment_done_by = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    date_of_comment = models.DateField(default=datetime.datetime.today)
    comment = models.TextField()

    def __str__(self):
        return str(self.id)


class ProductComments(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE)
    comment = models.ManyToManyField(Comment)

    def __str__(self):
        return str(self.id)


class Cart(models.Model):
    user_carted = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    product_carted = models.ForeignKey(Products, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_carted.user.username +" carted "+self.product_carted.name


class Chat(models.Model):
    date_of_chat = models.DateTimeField(default=datetime.datetime.now)
    send_by = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    chat = models.TextField()

    def __str__(self):
        return str(self.id)


class ChatRoom(models.Model):
    user1 = models.ForeignKey(CustomerUser, 
                related_name='user1', 
                on_delete=models.CASCADE
            )
    user2 = models.ForeignKey(CustomerUser, 
                related_name='user2', 
                on_delete=models.CASCADE
            )

    chat = models.ManyToManyField(Chat)

    def __str__(self):
        return "Chat room for {0} and {1}".format(
            self.user1.user.first_name,
            self.user2.user.first_name
        )


class PurchasedProducts(models.Model):
    buyer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    date_of_order = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return str(self.buyer.user.first_name) +" purchased "+ str(self.product.name)
