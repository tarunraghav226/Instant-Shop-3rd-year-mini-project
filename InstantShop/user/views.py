from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, UploadProductForm
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomerUser
from django.contrib import messages

# Create your views here.


class LoginView(View):

    def get(self, request):
        login_form = LoginForm()
        signup_form = SignUpForm()
        context = {'login_form':login_form,'signup_form':signup_form}
        if not request.user.is_authenticated:
            return render(request,'index.html', context)
        else:
            return render(request, 'index.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            login_form = LoginForm(request.POST)
            if login_form.validate_and_login(request):
                return redirect(reverse('index'))
            else:
                signup_form = SignUpForm()
                context = {'login_form':login_form,'signup_form':signup_form}
                return render(request,'index.html',context)
        else:
            return redirect(reverse('index'))

class RegisterView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            signup_form = SignUpForm(request.POST)
            login_form = LoginForm()

            if signup_form.is_valid():
                signup_form.save()
                return redirect(reverse('index'))
            else:
                context = {'login_form':login_form,
                            'signup_form': signup_form}
                return render(request, 'index.html', context)
        else:
            return redirect(reverse('index'))


class LogoutView(View, LoginRequiredMixin):
    def get(self, request):
        logout(request)
        return redirect(reverse('index'))


class EmailVerificationView(View):
    def get(self, request, **kwargs):
        token = kwargs['token']
        user = CustomerUser.objects.filter(token = token).first()
        if user is not None:
            messages.success(request,'Email verified successfully.')
            user.is_email_verified = True
            user.save()
        else:
            messages.error(request,'Wrong verification token.')
        return redirect(reverse('index'))


class ProfileView(LoginRequiredMixin,View):
    def get(self, request):
        return render(request, 'profile.html')

class UploadProductView(LoginRequiredMixin,View):
    def get(self, request):
        form = UploadProductForm()
        context = {'form':form}
        return render(request, 'product.html', context)

    def post(self, request):
        form = UploadProductForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect(reverse('upload-product'))
        else:
            context = {'form': form}
            return render(request, 'product.html',context)

class PreviousOrderDetailsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'previous-orders.html')