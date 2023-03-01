from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from applications.account import views

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('activate/<uuid:activation_code>/', views.ActivationAPIVIew.as_view()),
    path('register/', views.RegisterAPIView.as_view()),
    path('register_mentor/', views.MentorAPIView.as_view()),

    path('change_password/', views.ChangePasswordAPIView.as_view()),
    path('change_password_confirm/', views.ChangePasswordConfirmAPIView.as_view()),
]
