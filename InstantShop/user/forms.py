from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.core.exceptions import ValidationError
import datetime
from .models import CustomerUser, Products
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
        symbols_used = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@$&*'

        token = ''

        while True:
            for i in range(30):
                token += symbols_used[random.randint(0,len(symbols_used)-1)]
            break
        return token


class UploadProductForm(forms.Form):
    name = forms.CharField(max_length = 40, label="Name", widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'label':'Name'}
            ))

    description = forms.CharField(widget = forms.Textarea(
        attrs={
            'class':'form-control', 
            'label':'Description'}
            ))

    price = forms.DecimalField(max_digits = 5, decimal_places = 2, widget=forms.NumberInput(
        attrs={'class':'form-control',
        'label':'Name',
        'min':'0'
        }))

    features = forms.CharField(widget = forms.Textarea(
        attrs={'class':'form-control',
        'label':'Features'}
        ))

    months_of_product_used = forms.IntegerField(widget=forms.NumberInput(
        attrs={
            'class':'form-control',
            'label':'Months of product used',
            'min':'0',
            'max':'200'
        }
    ))

    img1 = forms.ImageField(label='Image 1 (required)', required = True, widget=forms.FileInput(attrs={
        'class':'form-control',
    }))

    img2 = forms.ImageField(label='Image 2',required = False, widget=forms.FileInput(attrs={
        'class':'form-control',
    }))

    img3 = forms.ImageField(label='Image 3',required = False, widget=forms.FileInput(attrs={
        'class':'form-control',
    }))
    
    img4 = forms.ImageField(label='Image 4',required = False, widget=forms.FileInput(attrs={
        'class':'form-control',
    }))

    def clean_name(self):
        name = self.cleaned_data['name']
        if name == '':
            raise ValidationError('Name cannot be empty.')
        else:
            return self.cleaned_data['name'] 
        
    def clean_description(self):
        description = self.cleaned_data['description']
        if description == '':
            raise ValidationError('Description cannot be empty.')
        else:
            return self.cleaned_data['description'] 

    def clean_price(self):
        prc = float(self.cleaned_data['price'])
        if prc >=0 :
            return self.cleaned_data['price']
        else:
            raise ValidationError('Price must be positive.')

    def clean_months_of_product_used(self):
        months = int(self.cleaned_data['months_of_product_used'])
        if months >=0 and months <= 200:
            return self.cleaned_data['months_of_product_used']
        else:
            raise ValidationError('Months must be between 0 and 200.')
    
    def clean_img1(self):
        photo = self.cleaned_data['img1']
        if photo and photo.size <= 700000:
            return self.cleaned_data['img1']
        else:
            raise ValidationError('Photo size must be less than 700kb.')
    
    def clean_img2(self):
        photo = self.cleaned_data['img2']

        if not photo:
            return self.cleaned_data['img2']

        if photo.size <= 700000:
            return self.cleaned_data['img2']
        else:
            raise ValidationError('Photo size must be less than 700kb.')

    def clean_img3(self):
        photo = self.cleaned_data['img3']

        if not photo:
            return self.cleaned_data['img3']

        if photo.size <= 700000:
            return self.cleaned_data['img3']
        else:
            raise ValidationError('Photo size must be less than 700kb.')
    
    def clean_img4(self):
        photo = self.cleaned_data['img4']

        if not photo:
            return self.cleaned_data['img4']

        if photo.size <= 700000:
            return self.cleaned_data['img4']
        else:
            raise ValidationError('Photo size must be less than 700kb.')

    def save(self, request):
        product = Products(
            user = request.user,
            name = self.cleaned_data['name'],
            description = self.cleaned_data['description'],
            price = self.cleaned_data['price'],
            features = self.cleaned_data['features'],
            months_of_product_used = self.cleaned_data['months_of_product_used'],
            product_uploaded_on_date = datetime.date.today(),
            img1 = self.cleaned_data['img1'],
            img2 = self.cleaned_data['img2'],
            img3 = self.cleaned_data['img3'],
            img4 = self.cleaned_data['img4'],
        )

        print(product.product_uploaded_on_date)
        product.save()
        return True



class UpdateProductForm(UploadProductForm):
    img1 = forms.ImageField(label='Image 1', required = False, widget=forms.FileInput(attrs={
        'class':'form-control',
    }))

    def clean_img1(self):
        photo = self.cleaned_data['img1']

        if not photo:
            return self.cleaned_data['img1']

        if photo.size <= 700000:
            return self.cleaned_data['img1']
        else:
            raise ValidationError('Photo size must be less than 700kb.')

    def save(self, id):
        products = Products.objects.filter(id = id)
        
        if len(products) > 0:
            product = products[0]

            product.name = self.cleaned_data['name']
            product.description = self.cleaned_data['description']
            product.price = self.cleaned_data['price']
            product.features = self.cleaned_data['features']
            product.months_of_product_used = self.cleaned_data['months_of_product_used']
            
            if self.cleaned_data['img1'] != '':
                product.img1 = self.cleaned_data['img1']
                
            if self.cleaned_data['img2'] != '':
                product.img2 = self.cleaned_data['img2']

            if self.cleaned_data['img3'] != '':
                product.img3 = self.cleaned_data['img3']
                
            if self.cleaned_data['img4'] != '':
                product.img1 = self.cleaned_data['img4']

            product.save()
            return True
        else:
            return False