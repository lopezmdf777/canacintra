from django import forms
from .models import Usuario, Publicacion, Archivo, PublicacionArchivo, Comentario
from django.contrib.auth.forms import UserCreationForm

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'foto']  # Solo campos que SÍ existan
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Tu usuario'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Tu correo'}),
            'foto': forms.TextInput(attrs={'placeholder': 'URL de tu foto (o selección)'})
        }

  
class PublicacionForm(forms.ModelForm):
  class Meta:
    model = Publicacion
    fields = ['titulo', 'resumen', 'contenido', 'foto_portada', 'fk_categoria']

class ComentarioForm(forms.ModelForm):
  class Meta:
    model = Comentario
    fields = ['contenido']
    widgets = {
      'contenido': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe un comentario...'}),
    }

