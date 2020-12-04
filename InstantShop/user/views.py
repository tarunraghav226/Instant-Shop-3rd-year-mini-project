from django.shortcuts import render, redirect
from .forms import LoginForm, SignUpForm, UploadProductForm, UpdateProductForm, ProfilePhotoForm, CommentForm
from django.views import View
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomerUser, Products, ProductComments, Cart, ChatRoom, Chat, PurchasedProducts
from django.contrib import messages
from modules.search import search
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core import serializers

# Create your views here.


class LoginView(View):
    """
        This view handles two request methods.
        GET method returns login and signup form if user is authenticated.
        POST method authenticates and log-in the user if authenticated.
    """

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
    """
        This view handles only one request method.
        POST method registers a user if details are valid.
    """
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
    """
        This view only handles one request method.
        GET method logs out the logged in user.
    """


    login_url='/index/'

    def get(self, request):
        logout(request)
        return redirect(reverse('index'))


class EmailVerificationView(View):
    """
        This view only handles one request method.
        GET method verifies the user email id.
    """

    def get(self, request, **kwargs):
        token = kwargs['token']
        user = CustomerUser.objects.filter(token = token)[0]
        if user is not None:
            messages.success(request,'Email verified successfully.')
            user.is_email_verified = True
            user.save()
        else:
            messages.error(request,'Wrong verification token.')
        return redirect(reverse('index'))


class ProfileView(LoginRequiredMixin,View):
    """
        This view only handles two request method.
        GET method renders the profile page with all the required details.
        POST method updates the user profile image.
    """

    login_url='/index/'

    def get(self, request):

        total_users = CustomerUser.objects.all().count()
        total_products = Products.objects.all().count()
        upload_by_user = Products.objects.filter(
            user=request.user
        ).count()
        total_purchased = PurchasedProducts.objects.filter(
            buyer = CustomerUser.objects.get(user=request.user)
        ).count()

        context = {
            'dp' : CustomerUser.objects.get(user = request.user).photo,
            'total_users' : total_users,
            'total_products' : total_products,
            'upload_by_user' : upload_by_user,
            'total_purchased' : total_purchased
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
    """
        This view only handles two request method.
        GET method gives the form to upload new products.
        POST method validates the form and adds new product in database.
    """

    login_url='/index/'

    def get(self, request):
        form = UploadProductForm()
        context = {            
            'form':form,
            'dp' : CustomerUser.objects.get(user = request.user).photo

        }
        return render(request, 'product.html', context)

    def post(self, request):
        form = UploadProductForm(request.POST, request.FILES)
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
    """
        This view only handles one request method.
        GET method gives information about orders of user and renders the html file.
    """

    login_url='/index/'

    def get(self, request):
        orders = PurchasedProducts.objects.filter(
            buyer = CustomerUser.objects.get(user = request.user)
        )

        context = {
            'dp' : CustomerUser.objects.get(user = request.user).photo,
            'orders' : orders
        }
        return render(request, 'previous-orders.html', context)


class UploadedProductsView(LoginRequiredMixin, View):
    """
        This view only handles two request method.
        GET method gives a list of products uploaded by user and renders the html file.
        POST method redirects to uploaded-products page.
    """

    login_url='/index/'

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
    """
        This view only handles one request method.
        GET method deletes the product requested by user.
    """

    login_url='/index/'

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
    """
        This view only handles two request method.
        GET method finds the correct product details and generates a form and then renders the html file.
        POST method validates the product form and updates the product details.
    """

    login_url='/index/'

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
    """
        This view only handles two request method.
        GET method generates login, signup form and list of all available products.
        POST method searches a particular product according to the user query.
    """


    def get(self, request):
        products = Products.objects.filter(selled=False)
        
        login_form = LoginForm()
        signup_form = SignUpForm()

        context = {
            'products' : products,
            'login_form':login_form,
            'signup_form':signup_form
        } 

        return render(request, 'shop.html', context)

    def post(self, request):
        search_text = request.POST['search-text']
        
        searched_list = search(search_text)

        login_form = LoginForm()
        signup_form = SignUpForm()

        context = {
            'login_form':login_form,
            'signup_form':signup_form
        }

        if len(searched_list) == 0:
            messages.error(request, 'No product found.')
        else:
            context['products'] = searched_list
        
        return render(request, 'shop.html', context)


class ProductView(View):
    """
        This view only handles one request method.
        GET method searches details about a specific product.
    """

    def get(self, request, **kwargs):
        id = kwargs['id']
        product = Products.objects.filter(id=id)
        
        if len(product) > 0:

            login_form = LoginForm()
            signup_form = SignUpForm()

            context ={
                'product' : product[0],
                'login_form':login_form,
                'signup_form':signup_form
            }

            comments = ProductComments.objects.filter(product=product[0])

            if len(comments) > 0:
                comments = comments[0].comment.all()
                context['comments'] = comments
 
            return render(request, 'product-view.html', context)
        else:
            messages.error(request, 'No Product found.')
            return redirect(reverse('shop'))


class AddCommentView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method allows user to add a comment on product.
    """

    login_url='/index/'

    def get(self, request, **kwargs):

        id = kwargs['id']

        comment_form = CommentForm({
            'comment' : request.GET['comment']
        })

        if comment_form.is_valid():
            comment_form.save(request = request, product_id = id)

        return redirect('/product-view/{0}'.format(id))


class AddProductToCartView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method adds a product to cart.
    """

    login_url = '/index/'

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

        checkPreviousCartItems = Cart.objects.filter(
            user_carted = cust_user,
            product_carted = product
        )

        if len(checkPreviousCartItems) == 0:
            Cart.objects.create(
                user_carted = cust_user,
                product_carted = product
            )

            messages.error(request, 'Product added to cart.')
        else:
            messages.error(request, 'Product is already in cart.')

        return redirect(reverse('shop'))


class ShowCartView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method shows all products in user cart.
    """

    login_url = '/index/'

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


class DeleteCartItemView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method deletes a product from cart.
    """

    login_url = '/index/'
    
    def get(self, request, **kwargs):
        cart_item_id = kwargs['id']
        cart_item = Cart.objects.filter(id=cart_item_id)

        if len(cart_item) > 0:
            cart_item = cart_item[0]

            if cart_item.user_carted.user == request.user:
                messages.info(request, "Cart item deleted successfully.")
                cart_item.delete()
            else:
                messages.error(request, "You are not authorised to delete this item.")
        else:
            messages.error(request, "Wrong request.")

        return redirect(reverse('show-cart'))


class ChatRoomView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method gives a list of all ChatRoom of the logged in user.
        POST method creates a ChatRoom if there none else redirects to chat-room.
    """

    login_url = '/index/'

    def get(self, request):
        rooms = ChatRoom.objects.filter(
            Q(user1 = CustomerUser.objects.get(user = request.user)) |
            Q(user2 = CustomerUser.objects.get(user = request.user))
        )

        context = {
            'rooms' : rooms
        }

        return render(request, 'chat.html', context)

    def post(self, request):
        user2 = request.POST['id']
        rooms = ChatRoom.objects.filter(
            Q(user1 = CustomerUser.objects.get(user = request.user),
            user2 = CustomerUser.objects.get(user = user2)) |
            Q(user1 = CustomerUser.objects.get(user = user2),
            user2 = CustomerUser.objects.get(user = request.user))
        )

        room = None
        if len(rooms) > 0:
            room = rooms[0]
        else:
            room = ChatRoom.objects.create(
                user1 = CustomerUser.objects.get(user = request.user),
                user2 = CustomerUser.objects.get(user = user2)
            )
    
        context = {
            'room_id':room.id,
        }

        return redirect(reverse('chat-room'))


class ChatView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method return JsonResponse of all the chats in a specific room.
        POST method adds a new chat in a specific room.
    """

    login_url = '/index/'

    def get(self, request):
        room_id = request.GET['id']

        rooms = ChatRoom.objects.filter(id = room_id)

        if len(rooms) > 0:
            room = rooms[0]
            chatsQuerySet = room.chat.all()
            chats = []
            for chat in chatsQuerySet:
                tempChat ={
                    'date':chat.date_of_chat,
                    'send_by':chat.send_by.user.id,
                    'chat':chat.chat
                }
                chats.append(tempChat)
            resData = {
                'chats' : chats
            }

            return JsonResponse(resData)
        else:
            messages.error('No room found.')
            return redirect(reverse('/chat/'))
    
    def post(self, request):
        room_id = request.POST['id']

        rooms = ChatRoom.objects.filter(id = room_id)

        if len(rooms) > 0:
            room = rooms[0]
            chat = Chat.objects.create(
                send_by = CustomerUser.objects.get(user = request.user),
                chat = request.POST['chat']
            )
            room.chat.add(chat)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class BuyProductView(LoginRequiredMixin, View):
    """
        This view only handles one request method.
        GET method adds a new product in users buyed product database.
    """

    login_url='/index/'

    def get(self, request, **kwargs):
        product_id = kwargs['id']

        buyer = CustomerUser.objects.get(user = request.user)
        products = Products.objects.filter(id=product_id,selled=False)

        if len(products) > 0:
            product = products[0]
            PurchasedProducts.objects.create(
                buyer = buyer,
                product = product
            )
            product.selled = True
            product.save()
            messages.info(request, "Product purchased successfully.")
        else:
            messages.error(request, "Wrong product request.")
        return redirect(reverse('shop'))


class AboutUsView(View):
    """
        This view only handles one request method.
        GET method generates login and signup form.
    """

    def get(self, request):
        login_form = LoginForm()
        signup_form = SignUpForm()
        
        context = {
            'login_form':login_form,
            'signup_form':signup_form
        }

        return render(request, 'about-us.html', context)
