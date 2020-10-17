from django.db import models
from django.contrib.auth.models import User

# Create your models here.

def user_directory(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.username,filename)

class CustomerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    dob = models.DateField()
    phone_number = models.TextField(max_length=13)
    photo = models.FileField(upload_to = user_directory, blank=True)
    token = models.CharField(max_length=30,primary_key=True)
    is_email_verified = models.BooleanField(default=False) 

    def __str__(self):
        return str(self.user.username)
