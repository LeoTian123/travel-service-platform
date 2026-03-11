from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.list_attractions),
    path('like/', views.like_attractions),
    path('unlike/', views.unlike_attractions),

    path('list_user/', views.list_attractions_user),

    path('list_UBCF/', views.get_UBCF),
]