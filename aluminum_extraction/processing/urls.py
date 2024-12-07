from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # For the built-in logout view

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('start_processing/<int:raw_material_id>/', views.start_processing, name='start_processing'),
    path('manage_byproducts/<int:processing_id>/', views.manage_byproducts, name='manage_byproducts'),
    path('register/', views.register, name='register'),
    path('access_denied/', views.access_denied, name='access_denied'),
    path('api/get_processing_data/<int:processing_id>/', views.get_processing_data, name='get_processing_data'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Add logout URL
]
 
