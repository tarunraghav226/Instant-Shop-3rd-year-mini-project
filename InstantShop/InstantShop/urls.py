"""InstantShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from user import views as view

from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', view.LoginView.as_view(), name='index'),
    path('register/', view.RegisterView.as_view(), name='register'),
    path('logout/', view.LogoutView.as_view(), name='logout'),
    path('about-us/', TemplateView.as_view(template_name='about-us.html'), name='about_us'),
    path('verify-email/<str:token>', view.EmailVerificationView.as_view(), name='verify_email'),
    path('shop/', TemplateView.as_view(template_name='shop.html'), name='shop'),
    path('profile/', view.ProfileView.as_view(), name='profile'),
    path('upload-product/', view.UploadProductView.as_view(), name='upload-product'),
    path('previous-orders/', view.PreviousOrderDetailsView.as_view(), name='previous-orders'),
    path('uploaded-products/', view.UploadedProductsView.as_view(), name='uploaded-products'),
    path('delete/<int:id>', view.DeleteProductView.as_view(), name='delete'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
