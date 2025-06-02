from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ----------------------- MANAGER USUARIO (opcional para autenticación) -------------------
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Si no se proporciona fk_rol, busca el id del rol admin
        if not extra_fields.get('fk_rol'):
            admin_rol = Rol.objects.get(nombre='admin')
            extra_fields['fk_rol'] = admin_rol
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)



# ----------------------- MODELOS ADAPTADOS A TU BASE DE DATOS ----------------------------

class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'rol'
        managed = False

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, db_column='id')  # << En tu BD es 'id', no 'id_usuario'
    username = models.CharField(max_length=100, unique=True, db_column='username')
    password = models.CharField(max_length=255, db_column='password')
    email = models.EmailField(unique=True, db_column='email')
    fk_rol = models.ForeignKey(Rol, on_delete=models.RESTRICT, db_column='fk_rol')
    foto = models.CharField(max_length=255, null=True, blank=True, db_column='foto')  # Es varchar, no ImageField
    # Quitar campos que no existen en la BD

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'usuario'
        managed = False  # Porque la tabla ya existe

class Categoria(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    nombre = models.CharField(max_length=100, db_column='nombre')
    # Quitar fk_usuario, no existe en la BD

    class Meta:
        db_table = 'categoria'
        managed = False

class Estatus(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    nombre = models.CharField(max_length=50, db_column='nombre')

    class Meta:
        db_table = 'statu'
        managed = False

class Publicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    titulo = models.CharField(max_length=255, db_column='titulo')
    resumen = models.TextField(null=True, db_column='resumen')
    contenido = models.TextField(db_column='contenido')
    fecha_creacion = models.DateTimeField(auto_now_add=False, db_column='fecha_creacion')  # La fecha la pone MySQL, no Django
    fecha_act = models.DateTimeField(auto_now_add=False, db_column='fecha_act')
    foto_portada = models.CharField(max_length=255, null=True, blank=True, db_column='foto_portada')
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='fk_usuario')
    fk_categoria = models.ForeignKey(Categoria, on_delete=models.RESTRICT, db_column='fk_categoria')
    fk_estatus = models.ForeignKey(Estatus, on_delete=models.RESTRICT, db_column='fk_estatus')
    visitas = models.IntegerField(default=0, db_column='visitas')

    class Meta:
        db_table = 'publicacion'
        managed = False

class Archivo(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    nombre = models.CharField(max_length=255, db_column='nombre')
    tipo = models.CharField(max_length=50, db_column='tipo', null=True)
    tamano = models.IntegerField(db_column='tamano', null=True)
    titulo = models.CharField(max_length=255, db_column='titulo', null=True)
    ruta = models.CharField(max_length=255, db_column='ruta')
    descripcion_corta = models.TextField(db_column='descripcion_corta', null=True)
    descripcion_larga = models.TextField(db_column='descripcion_larga', null=True)
    fk_usuario = models.ForeignKey('Usuario', on_delete=models.RESTRICT, db_column='fk_usuario')
    nombre_temporal = models.CharField(max_length=255, db_column='nombre_temporal', null=True)

    class Meta:
        db_table = 'archivo'
        managed = False


class Comentario(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    contenido = models.TextField(db_column='contenido')
    fk_usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, db_column='fk_usuario')
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion')
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion')
    fk_estatus = models.ForeignKey(Estatus, on_delete=models.RESTRICT, db_column='fk_estatus')
    fk_publicacion = models.ForeignKey(Publicacion, on_delete=models.RESTRICT, db_column='fk_publicacion')

    class Meta:
        db_table = 'comentario'
        managed = False

class PublicacionArchivo(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    fk_publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column='fk_publicacion')
    fk_archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE, db_column='fk_archivo')

    class Meta:
        db_table = 'publicacion_archivo'
        managed = False

