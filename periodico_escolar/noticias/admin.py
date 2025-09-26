from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Categoria, Noticia, Comentario, Reaccion, Edicion
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rol en el periódico escolar', {'fields': ('role',)}),
    )
    list_display = BaseUserAdmin.list_display + ('role',)
    list_filter = BaseUserAdmin.list_filter + ('role',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha', 'fecha_edicion')
    list_filter = ('categoria', 'autor__role')
    search_fields = ('titulo', 'contenido')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'noticia', 'fecha')
    list_filter = ('autor__role',)
    search_fields = ('contenido',)

@admin.register(Reaccion)
class ReaccionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'noticia')
    list_filter = ('tipo', 'usuario__role')

@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha')
    filter_horizontal = ('noticias',)