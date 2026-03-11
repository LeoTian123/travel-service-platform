from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.list_journals),
    path('like/', views.like_journals),
    path('unlike/', views.unlike_journals),

    path('list_user/', views.list_journals_user),

    path('list_detail/', views.list_journals_detail),

    path('list_attraction_id_and_name/', views.list_attraction_id_and_name),
    path('create/', views.create_journal),

    path('get_journal_image/<path:filename>', views.get_journal_image),
]