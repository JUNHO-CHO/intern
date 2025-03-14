from django.urls import path
from .views import signup, login, validate_token

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('validate_token/', validate_token, name='validate_token'),
]