from django.contrib import admin
from .models import (
    Usuario, Categoria, Publicacion, Archivo, Comentario,
    Rol, Estatus, PublicacionArchivo
)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']  # Solo esos campos existen

class PublicacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'fk_usuario', 'fk_estatus', 'fk_categoria', 'fecha_creacion', 'visitas']
    list_filter = ['fk_estatus', 'fk_categoria']
    search_fields = ['titulo']

class ArchivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'tipo', 'fk_usuario', 'ruta', 'descripcion_corta']
    search_fields = ['nombre']

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_usuario', 'fk_publicacion', 'fk_estatus', 'fecha_creacion']
    list_filter = ['fk_estatus']
    search_fields = ['contenido']

class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']

class EstatusAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']

class PublicacionArchivoAdmin(admin.ModelAdmin):
    list_display = ['id', 'fk_publicacion', 'fk_archivo']

# Registro en admin
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Publicacion, PublicacionAdmin)
admin.site.register(Archivo, ArchivoAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Rol, RolAdmin)
admin.site.register(Estatus, EstatusAdmin)
admin.site.register(PublicacionArchivo, PublicacionArchivoAdmin)
