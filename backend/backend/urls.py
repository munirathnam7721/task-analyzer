# backend/backend/urls.py (CORRECTED)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # CORRECT: Prefix the tasks app URLs with 'api/'
    path('api/', include('tasks.urls')), 
    
    # If you still want a root homepage, define it here (e.g., path('', HomeView.as_view(), name='home'))
]