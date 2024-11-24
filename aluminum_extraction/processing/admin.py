from django.contrib import admin

from django.contrib import admin
from .models import UserProfile, RawMaterial, Processing, ByProduct

admin.site.register(UserProfile)
admin.site.register(RawMaterial)
admin.site.register(Processing)
admin.site.register(ByProduct)
