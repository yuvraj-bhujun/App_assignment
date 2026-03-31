from django.urls import path
from django.contrib.auth import views as auth_views
from .shared_views import (
    CustomersPageView,
    DashboardView,
    CustomAdminLoginView,
    ReviewsPageView,
    ActivitiesPageView,
    BookingsPageView,
    PaymentsPageView,
    ActivityFormView,
    ActivityDeleteView,
    ActivityDetailView,
)
from . import views

urlpatterns = [
    path('admin/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/reviews/', ReviewsPageView.as_view(), name='reviews'),
    path('admin/reviews/delete/<int:review_id>', views.delete_review, name='delete_review'),
    path('admin/activities/', ActivitiesPageView.as_view(), name='activities'),
    path('admin/bookings/', BookingsPageView.as_view(), name='bookings'),
    path('admin/bookings/cancel/<int:booking_id>', views.cancel_booking, name='cancel_booking'),
    path('admin/payments/', PaymentsPageView.as_view(), name='payments'),
    path('admin/payments/report/pdf/', views.download_revenue_report, name='download_revenue_report'),
    path('admin/customers/', CustomersPageView.as_view(), name='customers_page'),
    path('admin/activity/add/', ActivityFormView.as_view(), name='add_activity'),
    path('admin/activity/delete/<int:pk>/', ActivityDeleteView.as_view(), name='delete_activity'),
    path('admin/login/', CustomAdminLoginView.as_view(), name='admin_login'),
    path('aboutus/', views.about_us_view, name='about_us'),
    path('', views.homepage, name='homepage'),
    path('user/bookings/', views.profile_booking, name='profile_booking'),
    path('user/review/<int:booking_id>/', views.review, name='review'),
    path('user/notifications/', views.notifications, name='notifications'),
    path('user/activity/<str:activity_name>/', ActivityDetailView.as_view(), name='activity_detail'),
    path('user/payment/<str:activity_name>/', views.payment, name='payment'),
    path('user/profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/activity/', views.activity_list, name='activity_list'),
    path('contact/', views.contact, name='contact'),
    
    # User cancel booking
    path('user/booking/cancel/<int:booking_id>/', views.user_cancel_booking, name='user_cancel_booking'),

    # Password Reset (for forgotten passwords)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='password_reset_form.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    path('signup/termsandcondition/', views.terms_and_condition, name='termsandcondition'),
]
