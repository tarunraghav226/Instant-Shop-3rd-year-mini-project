from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.core.exceptions import ValidationError
import datetime
from .models import CustomerUser
from django.core.mail import send_mail
from modules.mail import mail
from django.contrib import messages

import random


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20,label="Username ")
    password = forms.CharField(max_length=20, label='Password ', widget = forms.PasswordInput)


    def clean(self):
        user = authenticate(username=self.cleaned_data['username'],
                password = self.cleaned_data['password']
        )

        if user:
            return self.cleaned_data
        else:
            raise ValidationError("Username or Password not matched.")

    def validate_and_login(self, request):
        if self.is_valid() and self.clean():
            user = authenticate(username=self.cleaned_data['username'],
                password = self.cleaned_data['password']
            )
            login(request,user)

            cust_user = CustomerUser.objects.get(user = user)
            
            if not cust_user.is_email_verified:
                messages.error(request,'Please verify your mail id.')

            return True
        else:
            return False


class SignUpForm(forms.Form):
    firstname = forms.CharField(max_length=20, label='FirstName')
    lastname = forms.CharField(max_length=20, label='LastName')
    username = forms.CharField(max_length=20, label='UserName')
    address = forms.CharField(max_length=20, label='Address')
    email = forms.CharField(max_length=70, label='Email', widget=forms.EmailInput)
    tel = forms.CharField(label='Mobile Number', widget=forms.TextInput(attrs={'pattern':'\d{10,12}','title':'Must have 10 digits.'}))
    dob = forms.DateField(label='Date Of Birth', widget=forms.DateInput(attrs={'id':'datepicker', 'type':'date'}))
    password1 = forms.CharField(max_length=20,label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=20,label='Confirm Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            raise ValidationError('Username already taken.')
        except ValidationError:
            raise ValidationError('Username already taken.')
        except:
            return self.cleaned_data['username']
    

    def clean_password2(self):
        return self.cleaned_data['password2']

    def clean_password1(self):
        if len(self.cleaned_data['password1'])<8:
            raise ValidationError('Password length must be atleast 8 characters long.')

        if self.cleaned_data['password1'].isnumeric():
            raise ValidationError('Password must contain alphabets.')

        return self.cleaned_data['password1']

    def clean(self):

        dob = self.cleaned_data['dob']
        
        dob = datetime.datetime.strptime(str(dob),'%Y-%m-%d')
        now = datetime.datetime.now()
        
        if (now-dob).days/365 < 15:
            raise ValidationError('Year must be 15 years old to use this site.')

        return self.cleaned_data

    def save(self):

        token = self.generate_token()

        user = User.objects.create(first_name = self.cleaned_data['firstname'],
                    last_name = self.cleaned_data['lastname'],
                    email = self.cleaned_data['email'],
                    username = self.cleaned_data['username']
        )

        user.set_password(self.cleaned_data['password1'])

        user.save()

        cust_user = CustomerUser(user = user,
                                 address = self.cleaned_data['address'],
                                 dob = self.cleaned_data['dob'],
                                 phone_number = self.cleaned_data['tel'],
                                 token = token
        )

        cust_user.save()

        mail(user.email,user.first_name,token)

    def generate_token(self):
        symbols_used = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$&*'

        token = ''

        while True:
            for i in range(30):
                token += symbols_used[random.randint(0,len(symbols_used)-1)]
            break
        return token