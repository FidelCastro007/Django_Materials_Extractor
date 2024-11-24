# aluminum_extraction/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('processing/', include('processing.urls')),  # Include processing app's URLs
    path('login/', auth_views.LoginView.as_view(template_name='processing/login.html'), name='login'),
    path('', include('processing.urls')),  # Include the processing app's URL for the homepage
]
