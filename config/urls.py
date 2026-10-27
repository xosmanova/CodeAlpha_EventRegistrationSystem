"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include

# Customize Admin Site branding
admin.site.site_header = "CodeAlpha Event Registration Portal"
admin.site.site_title = "CodeAlpha Event Admin"
admin.site.index_title = "Event & Registration Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
]
