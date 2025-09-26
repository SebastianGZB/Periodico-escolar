from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [('lector','Lector'), ('redactor','Redactor'), ('editor','Editor'), ('admin', 'Administrador'),]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lector')
    def is_redactor(self): return self.role == 'redactor'
    def is_editor(self):   return self.role == 'editor'
    def is_lector(self):   return self.role == 'lector'
    def is_admin(self):    return self.role == 'admin'

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_edicion = models.DateTimeField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='noticias/', null=True, blank=True)
    def save(self, *args, **kwargs):
        if self.pk: self.fecha_edicion = timezone.now()
        super().save(*args, **kwargs)
    def __str__(self): return self.titulo

class Comentario(models.Model):
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    def __str__(self): return f'Comentario de {self.autor} en {self.noticia.titulo}'

class Reaccion(models.Model):
    TIPO = [('like','👍'), ('dislike','👎')]
    tipo = models.CharField(max_length=10, choices=TIPO)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    def __str__(self): return f'{self.tipo} de {self.usuario} en {self.noticia.titulo}'

class Edicion(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=200)
    noticias = models.ManyToManyField(Noticia)
    def __str__(self): return f"{self.titulo} ({self.fecha.strftime('%d-%m-%Y %H:%M')})"

class ColaboracionNoticia(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noticia = models.ForeignKey('Noticia', on_delete=models.CASCADE, related_name='colaboraciones')
    puede_editar = models.BooleanField(default=False)
    puede_publicar = models.BooleanField(default=False)  # por si luego agregas estado 'published'

    class Meta:
        unique_together = ('usuario', 'noticia')  # un registro por usuario/artículo

    def __str__(self):
        return f"{self.usuario.username} ↔ {self.noticia.titulo} (editar={self.puede_editar}, publicar={self.puede_publicar})"

imagen = models.ImageField(upload_to='noticias/', null=True, blank=True)