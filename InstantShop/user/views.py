from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, UploadProductForm, UpdateProductForm, ProfilePhotoForm
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomerUser, Products
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
        context = {
            'dp' : CustomerUser.objects.get(user = request.user).photo
        }
        return render(request, 'profile.html', context)
    
    def post(self, request):
        form = ProfilePhotoForm(request.POST, request.FILES)
        if form.is_valid():
            if form.save(request.user):
                messages.error(request, 'Updated successfully.')
            else:
                messages.error(request, 'Something went wrong.')
        else:
            messages.error(request, "Either you didn't uploaded a photo or photo must not exceed 700kb size.")
        return redirect(reverse('profile'))

class UploadProductView(LoginRequiredMixin,View):
    def get(self, request):
        form = UploadProductForm()
        context = {            
            'form':form,
            'dp' : CustomerUser.objects.get(user = request.user).photo

        }
        return render(request, 'product.html', context)

    def post(self, request):
        form = UploadProductForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect(reverse('upload-product'))
        else:
            context = {
                'form': form,
                'dp' : CustomerUser.objects.get(user = request.user).photo
            }
            return render(request, 'product.html',context)

class PreviousOrderDetailsView(LoginRequiredMixin, View):
    def get(self, request):
        context={
            'dp' : CustomerUser.objects.get(user = request.user).photo
        }
        return render(request, 'previous-orders.html')


class UploadedProductsView(LoginRequiredMixin, View):
    def get(self, request):
        products = Products.objects.filter(user=request.user)
        context = {
            'products':products,
            'dp' : CustomerUser.objects.get(user = request.user).photo
        }
        return render(request, 'uploaded-products.html', context)

    def post(self, request):
        return redirect(reverse('uploaded-products'))

class DeleteProductView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        products = Products.objects.filter(id = kwargs['id'])

        if len(products) > 0:
            product = products[0]
            if product.user == request.user:
                product.delete()
                messages.info(request, 'Product deleted successfully.')
            else:
                messages.error(request, 'You cannot delete this product.')
        else:
            messages.info(request, 'Wrong product request.')
        return redirect(reverse('uploaded-products'))


class EditProductView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        products = Products.objects.filter(id = kwargs['id'])

        if len(products) > 0:
            product = products[0]
            if product.user == request.user:
                data = {
                    'name' : product.name,
                    'description' : product.description,
                    'price' : product.price,
                    'features' : product.features,
                    'months_of_product_used' : product.months_of_product_used,
                    'img1' : product.img1,
                    'img2' : product.img2,
                    'img3' : product.img3,
                    'img4' : product.img4,
                }

                update_product_form = UpdateProductForm(data = data)
                
                context = {
                    'form':update_product_form,
                    'id' : product.id,
                    'dp' : CustomerUser.objects.get(user = request.user).photo
                }
                
                return render(request, 'edit-product.html', context)
            else:
                messages.error(request, 'You are not authorized to update this product.')
                return redirect(reverse('uploaded-products'))
        else:
            messages.error(request, 'Wrong product request.')
        return redirect(reverse('uploaded-products'))

    def post(self, request, **kwargs):

        products = Products.objects.filter(id = kwargs['id'])
        
        if len(products) > 0:
            product = products[0]
            if product.user == request.user:
                form = UpdateProductForm(request.POST, request.FILES)
                if form.is_valid():
                    print(request.POST)
                    if form.save(kwargs['id']):
                        messages.error(request, 'Product updated successfully.')
                    else:
                        messages.error(request, 'Something went wrong.')
                else:
                    context = {
                        'form' : form,
                        'id' : product.id,
                        'dp' : CustomerUser.objects.get(user = request.user).photo
                    }
                    return render(request, 'edit-product.html', context)
            else:
                messages.error('You are not authorized to edit this product.')
        else:
            messages.error(request, 'Wrong product request.')
        return redirect(reverse('uploaded-products'))

class ShowProductView(View):

    def get(self, request):
        products = Products.objects.all()
        
        context = {
            'products' : products,
        } 

        return render(request, 'shop.html', context)