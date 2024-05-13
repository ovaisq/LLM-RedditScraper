from django.urls import path
from .views import post_detail

urlpatterns = [
    path('post-detail/', post_detail, name='post_detail'),
    
]

