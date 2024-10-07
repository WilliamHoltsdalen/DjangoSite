from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('landing/', views.landing_page_view, name='landing_page'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('balance/', views.check_balance_view, name='check_balance'),
    path('settings/', views.account_settings_view, name='account_settings'),
    path('settings/delete_account/<int:account_id>/', views.delete_bank_account_view, name='delete_bank_account'),
    path('settings/delete_address_book/<int:address_book_id>/', views.delete_address_book_entry_view, name='delete_address_book_entry'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('error/', views.error_view, name='error'),
    path('success/', views.success_view, name='success'),
]
