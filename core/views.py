from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Publicacion, Usuario, Estatus, Rol, PublicacionArchivo, Categoria, Archivo, Comentario
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import EditarPerfilForm, PublicacionForm, ComentarioForm
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.timezone import now
from datetime import datetime
from django.views.decorators.http import require_POST
from django.contrib.auth.models import BaseUserManager

User = get_user_model()

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, fk_rol=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, fk_rol=fk_rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
def home(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('index')
    else:
      messages.error(request, "Credenciales inválidas")

  publicaciones = Publicacion.objects.filter(fk_estatus__nombre='PUBLICADA').order_by('-fecha_creacion')[:4]
  return render(request, 'core/index.html', {'publicaciones': publicaciones})

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
        else:
            try:
                # Obtener el rol LECTOR por defecto
                rol_lector = Rol.objects.get(nombre__iexact='Lector')

                # Crear usuario con ese rol
                user = User(
                    username=username,
                    email=email,
                    fk_rol=rol_lector
                )
                user.set_password(password)
                user.save()

                login(request, user)
                return redirect('index')

            except Rol.DoesNotExist:
                messages.error(request, "No se encontró el rol Lector en la base de datos.")
            except Exception as e:
                messages.error(request, f"Error al guardar el usuario: {e}")

    return render(request, 'core/registro.html')

# Función auxiliar para obtener el rol del usuario autenticado
def get_user_role(user):
 if hasattr(user, 'fk_rol') and user.fk_rol:
  return user.fk_rol.nombre.lower()
 return None


# Decorador personalizado para controlar acceso por rol
def role_required(roles=[]):
 def decorator(view_func):
  def _wrapped_view(request, *args, **kwargs):
   if not request.user.is_authenticated:
    return redirect('login')
   role = get_user_role(request.user)
   if role in roles:
    return view_func(request, *args, **kwargs)
   return redirect('index') 
  return _wrapped_view
 return decorator

# Ver publicación específica
def ver_publicacion(request, id):
  publicacion = get_object_or_404(Publicacion, id_publicacion=id)

  # Verifica si ya se contó la vista en esta sesión
  session_key = f'vista_publicacion_{publicacion.id_publicacion}'
  if not request.session.get(session_key, False):
    publicacion.vistas += 1
    publicacion.save(update_fields=['vistas'])
    request.session[session_key] = True

  galeria = PublicacionArchivo.objects.filter(fk_publicacion=publicacion)

  comentarios = Comentario.objects.filter(
    fk_publicacion=publicacion,
    fk_estatus__nombre='PUBLICADA'
  ).order_by('fecha_creacion')

  return render(request, 'core/ver_publicacion.html', {
    'publicacion': publicacion,
    'galeria': galeria,
    'comentarios': comentarios
  })

  
# Panel de control 
@login_required(login_url='login')
@role_required(roles=['operador', 'admin'])
def panel_control(request):
  seccion = request.GET.get('seccion', 'publicaciones')

  publicaciones_revision = Publicacion.objects.filter(fk_estatus__nombre__iexact='Revisión')
  publicaciones_aceptadas = Publicacion.objects.filter(fk_estatus__nombre__iexact='Publicada')
  publicaciones_rechazadas = Publicacion.objects.filter(fk_estatus__nombre__iexact='Rechazada')
  publicaciones_archivadas = Publicacion.objects.filter(fk_estatus__nombre__iexact='Archivada')

  comentarios_pendientes = Comentario.objects.filter(fk_estatus__nombre__iexact='Revisión')
  comentarios_aceptados = Comentario.objects.filter(fk_estatus__nombre__iexact='Publicada')

  usuarios = Usuario.objects.all().order_by('-id')

  # Si se está en la sección "roles", agrupar usuarios por rol
  usuarios_por_rol = {}
  roles_disponibles = Rol.objects.all()

  if seccion == 'roles':
    for rol in roles_disponibles:
      usuarios_por_rol[rol.nombre] = Usuario.objects.filter(fk_rol=rol).order_by('-id')

  return render(request, 'core/panel_control.html', {
    'seccion': seccion,
    'publicaciones_revision': publicaciones_revision,
    'publicaciones_aceptadas': publicaciones_aceptadas,
    'publicaciones_rechazadas': publicaciones_rechazadas,
    'publicaciones_archivadas': publicaciones_archivadas,
    'comentarios_pendientes': comentarios_pendientes,
    'comentarios_aceptados': comentarios_aceptados,
    'usuarios': usuarios,
    'usuarios_por_rol': usuarios_por_rol,
    'roles_disponibles': roles_disponibles
  })


# Crear publicación (editor y admin)
@login_required(login_url='login')
@role_required(roles=['editor', 'admin'])
def crear_publicacion(request):
  if request.method == 'POST':
    form = PublicacionForm(request.POST, request.FILES)
    galeria = request.FILES.getlist('galeria')

    if form.is_valid():
      publicacion = form.save(commit=False)
      publicacion.fk_usuario = request.user
      publicacion.fk_estatus = Estatus.objects.get(nombre='REVISION')
      publicacion.fecha_creacion = timezone.now()

      if 'foto_portada' in request.FILES:
        publicacion.foto_portada = request.FILES['foto_portada']

      publicacion.save()

      for archivo in galeria:
        ruta_guardado = default_storage.save(f'archivos/{archivo.name}', ContentFile(archivo.read()))

        archivo_obj = Archivo.objects.create(
          nombre_archivo=archivo.name,
          nombre_temporal=archivo.name,
          ruta_archivo=ruta_guardado,
          tipo_archivo=archivo.content_type,
          tamano=archivo.size,
          fk_usuario=request.user,
          fecha_creacion=timezone.now(),
          fecha_actualizacion=timezone.now()
        )

        PublicacionArchivo.objects.create(
          fk_publicacion=publicacion,
          fk_archivo=archivo_obj,
          fk_usuario=request.user,
          fecha_creacion=timezone.now(),
          fecha_actualizacion=timezone.now()
        )

      return redirect('index')

  else:
    form = PublicacionForm()

  archivos = Archivo.objects.filter(fk_usuario=request.user, tipo_archivo__startswith='image')
  categorias = Categoria.objects.all()

  return render(request, 'core/crear_publicacion.html', {
    'form': form,
    'archivos': archivos,
    'categorias': categorias,
  })


# Buscar publicaciones (todos)
def buscar(request):
 query = request.GET.get('q', '')
 resultados = Publicacion.objects.filter(titulo__icontains=query, fk_estatus__nombre='PUBLICADA')
 return render(request, 'core/busqueda.html', {'resultados': resultados, 'query': query})

def noticias(request):
 categoria_id = request.GET.get('categoria')
 publicaciones = Publicacion.objects.filter(fk_estatus__nombre='PUBLICADA')

 if categoria_id:
  publicaciones = publicaciones.filter(fk_categoria__id_categoria=categoria_id)

 publicaciones = publicaciones.order_by('-fecha_creacion')
 categorias = Categoria.objects.all()
 paginator = Paginator(publicaciones, 6)
 page_number = request.GET.get('page')
 page_obj = paginator.get_page(page_number)

 return render(request, 'core/noticias.html', {
  'page_obj': page_obj,
  'categorias': categorias
 })


def acerca(request):
 return render(request, 'core/acerca.html')

@login_required
def perfil(request):
  publicaciones = Publicacion.objects.filter(fk_usuario=request.user, fk_estatus__nombre="PUBLICADA").order_by('-fecha_creacion')
  return render(request, 'core/perfil.html', {
    'user': request.user,
    'publicaciones': publicaciones,
  })


class CambiarContrasenaView(LoginRequiredMixin, PasswordChangeView):
 template_name = 'core/cambiar_contrasena.html'
 success_url = reverse_lazy('index')

@login_required
def editar_perfil(request):
 user = request.user

 if request.method == 'POST':
  form = EditarPerfilForm(request.POST, request.FILES, instance=user)
  if form.is_valid():
   perfil = form.save(commit=False)
   perfil.save()
   return redirect('perfil')
 else:
  form = EditarPerfilForm(instance=user)

 return render(request, 'core/editar_perfil.html', {'form': form})

@login_required
def comentar(request, id_publicacion):
  publicacion = get_object_or_404(Publicacion, id_publicacion=id_publicacion)

  if request.method == 'POST':
   contenido = request.POST.get('contenido')
  if contenido:
    Comentario.objects.create(
      contenido=contenido,
      fk_usuario=request.user,
      fk_publicacion_id=id_publicacion,
      fk_estatus=Estatus.objects.get(nombre='REVISIÓN'),
      fecha_creacion=timezone.now(),
      fecha_actualizacion=timezone.now()
    )
    messages.info(request, "Tu comentario fue enviado y será publicado tras revisión.")
  return redirect('ver_publicacion', id=id_publicacion)
  
def perfil_publico(request, id):
  usuario = Usuario.objects.get(id=id)
  publicaciones = Publicacion.objects.filter(fk_usuario=usuario, fk_estatus__nombre='PUBLICADA').order_by('-fecha_creacion')
  return render(request, 'core/perfil_publico.html', {
    'usuario': usuario,
    'publicaciones': publicaciones
  })

def aprobar_publicacion(request, id):
  publicacion = get_object_or_404(Publicacion, pk=id)
  publicacion.fk_estatus_id = Estatus.objects.get(nombre__iexact='PUBLICADA').id_estatus
  publicacion.save()
  return redirect('/panel/?seccion=publicaciones')

def rechazar_publicacion(request, id):
  publicacion = get_object_or_404(Publicacion, pk=id)
  publicacion.fk_estatus_id = Estatus.objects.get(nombre__iexact='RECHAZADA').id_estatus
  publicacion.save()
  return redirect('/panel/?seccion=publicaciones')

def archivar_publicacion(request, id):
  publicacion = get_object_or_404(Publicacion, pk=id)
  publicacion.fk_estatus_id = Estatus.objects.get(nombre__iexact='ARCHIVADA').id_estatus
  publicacion.save()
  return redirect('/panel/?seccion=publicaciones')

def aprobar_comentario(request, id):
  comentario = get_object_or_404(Comentario, pk=id)
  estatus_publicado = Estatus.objects.get(nombre__iexact='PUBLICADA')
  comentario.fk_estatus = estatus_publicado
  comentario.save()
  return redirect('/panel/?seccion=comentarios')

def rechazar_comentario(request, id):
  comentario = get_object_or_404(Comentario, pk=id)
  estatus_rechazado = Estatus.objects.get(nombre__iexact='RECHAZADA')
  comentario.fk_estatus = estatus_rechazado
  comentario.save()
  return redirect('/panel/?seccion=comentarios')

@require_POST
def cambiar_rol_usuario(request, id_usuario):
  usuario = get_object_or_404(Usuario, pk=id_usuario)
  nuevo_rol_id = request.POST.get('nuevo_rol')

  if nuevo_rol_id:
    nuevo_rol = get_object_or_404(Rol, pk=nuevo_rol_id)
    usuario.fk_rol = nuevo_rol
    usuario.save()
  
  return redirect('/panel/?seccion=roles')
 
@login_required
def editar_publicacion(request, id):
  publicacion = get_object_or_404(Publicacion, id_publicacion=id)

  if request.method == 'POST':
    form = PublicacionForm(request.POST, request.FILES, instance=publicacion)
    galeria = request.FILES.getlist('galeria')
    imagenes_eliminadas = request.POST.get('imagenes_eliminadas', '')

    if form.is_valid():
      publicacion = form.save(commit=False)
      publicacion.contenido = request.POST.get('contenido')
      publicacion.fecha_actualizacion = timezone.now()
      publicacion.save()

      # Eliminar imágenes si el usuario lo solicitó
      if imagenes_eliminadas:
        ids_eliminar = [int(i) for i in imagenes_eliminadas.split(',') if i.isdigit()]
        for id_pa in ids_eliminar:
          pa = PublicacionArchivo.objects.filter(id=id_pa).first()
          if pa:
            archivo = pa.fk_archivo
            pa.delete() # elimina la relación

            # Verifica si ese archivo ya no se usa en ninguna otra publicación
            if not PublicacionArchivo.objects.filter(fk_archivo=archivo).exists():
              archivo.ruta_archivo.delete(save=False) # elimina del sistema de archivos
              archivo.delete() # elimina el registro

      # Subir nuevas imágenes
      for archivo in galeria:
        ruta_guardado = default_storage.save(f'archivos/{archivo.name}', ContentFile(archivo.read()))
        archivo_obj = Archivo.objects.create(
          nombre_archivo=archivo.name,
          nombre_temporal=archivo.name,
          ruta_archivo=ruta_guardado,
          tipo_archivo=archivo.content_type,
          tamano=archivo.size,
          fk_usuario=request.user,
          fecha_creacion=timezone.now(),
          fecha_actualizacion=timezone.now()
        )
        PublicacionArchivo.objects.create(
          fk_publicacion=publicacion,
          fk_archivo=archivo_obj,
          fk_usuario=request.user,
          fecha_creacion=timezone.now(),
          fecha_actualizacion=timezone.now()
        )

      return redirect('ver_publicacion', id=publicacion.id_publicacion) 

  else:
    form = PublicacionForm(instance=publicacion)

  categorias = Categoria.objects.all()
  galeria = PublicacionArchivo.objects.filter(fk_publicacion=publicacion)

  return render(request, 'core/editar_publicacion.html', {
    'form': form,
    'publicacion': publicacion,
    'categorias': categorias,
    'galeria': galeria,
  })