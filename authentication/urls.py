from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.SendOtp.as_view()),
    path('loginotp/', views.LoginOtp.as_view()),
    path('loginpass/', views.LoginPass.as_view()),
    # forget
    path('forgetPass/', views.ForgetPass.as_view()),
    # signup
    path('signUp/', views.SignUp.as_view({'put': 'update'})),
]
