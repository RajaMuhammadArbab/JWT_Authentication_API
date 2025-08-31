from django.urls import path
from .views import register, LoginAPIView, RefreshAPIView, LogoutAPIView, ProtectedAPIView

urlpatterns = [
    path("register/", register, name="register"),
    path('login/', LoginAPIView.as_view(), name='login'),
    path("token/refresh/",RefreshAPIView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('protected/', ProtectedAPIView.as_view(), name='protected'),
]
