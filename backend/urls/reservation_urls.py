from django.urls import path
from backend.views import reservation_views as views

urlpatterns = [
        
    path('add/', views.add_reservation, name='add-reservation'),

]