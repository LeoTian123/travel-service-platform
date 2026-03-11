from django.urls import path

from . import views

urlpatterns = [
    path('list_graph/', views.list_graph),
    path('best_path_dijkstra/', views.best_path_dijkstra),
    path('best_path_circuit/', views.best_path_circuit),
    path('radar_search/', views.radar_search),
]