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
    path('add_raw_material/', views.add_raw_material, name='add_raw_material'),
    path('add_processing/', views.add_processing, name='add_processing'),
    path('add_byproduct/', views.add_byproduct, name='add_byproduct'),
    path('register_user/', views.register_user, name='register_user'),
    path('delete_raw_material/<int:raw_material_id>/', views.delete_raw_material, name='delete_raw_material'),
    path('delete_byproduct/<int:byproduct_id>/', views.delete_byproduct, name='delete_byproduct'),
    path('edit_raw_material/<int:raw_material_id>/', views.edit_raw_material, name='edit_raw_material'),
    path('edit_byproduct/<int:byproduct_id>/', views.edit_byproduct, name='edit_byproduct'),
    path('byproduct/<int:byproduct_id>/', views.byproduct_details, name='byproduct_details'),
    path('reset-auto-increment/', views.reset_auto_increment, name='reset_auto_increment'),
]
 
