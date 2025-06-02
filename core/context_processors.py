# core/context_processors.py
from .models import Publicacion

def publicaciones_footer(request):
  publicaciones = Publicacion.objects.filter(fk_estatus__nombre='PUBLICADA').order_by('-fecha_creacion')
  return {'publicaciones_footer': publicaciones}

