from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
  path('', include('core.urls')),
  path('tinymce/', include('tinymce.urls')),
  path('admin/', admin.site.urls),
  path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
  path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
