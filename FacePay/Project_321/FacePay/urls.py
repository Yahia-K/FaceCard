from django.contrib import admin
from django.urls import path
from . import views
from .views import recharge_wallet
from .views import proceed_to_payment

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Main Pages
    path('home/', views.home, name='home'),
    path('homepage/', views.homepage, name='homepage'),
    path('parent/', views.parent, name='parent'),
    path('workpanel/', views.workpanel_view, name='workpanel'),

    # POS & Canteen
    path('pos/', views.pos_view, name='pos'),
    path('canteen/', views.canteen_view, name='canteen'),
    path('process_payment/', proceed_to_payment, name='process_payment'),



    #Add kid & Face Scanning
    path('scan_face/', views.scan_face, name='scan_face'),
    path('addkid/', views.addkid, name='addkid'),
    path('scan_customer_face/', views.scan_customer_face, name='scan_customer_face'),



    # Additional Views
    path('clogin/', views.clogin_view, name='clogin'),
    path("recharge_wallet/", recharge_wallet, name="recharge_wallet"),


]


