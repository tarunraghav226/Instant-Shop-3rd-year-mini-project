from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, UploadProductForm, UpdateProductForm, ProfilePhotoForm, CommentForm
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomerUser, Products, ProductComments, Cart
from django.contrib import messages
from modules.search import search

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

    def post(self, request):
        search_text = request.POST['search-text']
        
        searched_list = search(search_text)

        context = {}

        if len(searched_list) == 0:
            messages.error(request, 'No product found.')
        else:
            context = {
                'products' : searched_list
            }
        
        return render(request, 'shop.html', context)

class ProductView(View):
    def get(self, request, **kwargs):
        id = kwargs['id']
        product = Products.objects.filter(id=id)
        
        if len(product) > 0:

            context ={
                'product' : product[0],
            }

            comments = ProductComments.objects.filter(product=product[0])

            if len(comments) > 0:
                print(comments[0].comment.all())
                comments = comments[0].comment.all()
                context['comments'] = comments
 
            return render(request, 'product-view.html', context)
        else:
            messages.error(request, 'No Product found.')
            return redirect(reverse('shop'))


class AddCommentView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):

        id = kwargs['id']

        comment_form = CommentForm({
            'comment' : request.GET['comment']
        })

        if comment_form.is_valid():
            comment_form.save(request = request, product_id = id)

        return redirect('/product-view/{0}'.format(id))


class AddProductToCartView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):

        product_id = kwargs['id']

        cust_user = CustomerUser.objects.filter(user = request.user)
        product = Products.objects.filter(id = product_id)

        if len(product) > 0:
            product = product[0]
        else:
            messages.error(request, 'Product not found.')
            return redirect(reverse('shop'))

        if len(cust_user) > 0:
            cust_user = cust_user[0]
        else:
            messages.error(request, 'Not a valid user.')
            return redirect(reverse('shop')) 

        Cart.objects.create(
            user_carted = cust_user,
            product_carted = product
        )

        messages.error(request, 'Product added to cart.')
        return redirect(reverse('shop'))


class ShowCartView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart.objects.filter(
            user_carted = CustomerUser.objects.get(
                user = request.user
            )
        )

        context = {}
        if len(cart) > 0:
            context = {
                'items' : cart
            }    
        return render(request, 'cart.html', context)