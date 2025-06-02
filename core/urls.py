from django.urls import path
from . import views
from core.views import *
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView

urlpatterns = [
  path('', views.home, name='index'),
  path('publicacion/<int:id>/', views.ver_publicacion, name='ver_publicacion'),
  path('panel/', views.panel_control, name='panel_control'),
  path('crear/', views.crear_publicacion, name='crear_publicacion'),
  path('buscar/', views.buscar, name='buscar'),
  path('registro/', views.registro, name='registro'),
  path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
  path('noticias/', views.noticias, name='noticias'),
  path('acerca/', views.acerca, name='acerca'),
  path('perfil/', views.perfil, name='perfil'),
  path('cambiar-contrasena/', CambiarContrasenaView.as_view(), name='cambiar_contrasena'),
  path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
  path('comentario/<int:id_publicacion>/', views.comentar, name='comentar'),
  path('perfil/<int:id>/', views.perfil_publico, name='perfil_publico'),
  path('publicacion/<int:id>/aprobar/', views.aprobar_publicacion, name='aprobar_publicacion'),
  path('publicacion/<int:id>/rechazar/', views.rechazar_publicacion, name='rechazar_publicacion'),
  path('publicacion/<int:id>/archivar/', views.archivar_publicacion, name='archivar_publicacion'),
  path('comentario/<int:id>/aprobar/', views.aprobar_comentario, name='aprobar_comentario'),
  path('comentario/<int:id>/rechazar/', views.rechazar_comentario, name='rechazar_comentario'),
  path('cambiar-rol/<int:id_usuario>/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
  path('editar-publicacion/<int:id>/', views.editar_publicacion, name='editar_publicacion'),
  path('login/', auth_views.LoginView.as_view(), name='login'),
]
