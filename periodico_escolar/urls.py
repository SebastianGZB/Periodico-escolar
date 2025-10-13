from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from noticias import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página principal
    path('', views.inicio, name='inicio'),

    # Noticias (CRUD mínimo)
    path('crear/', views.crear_noticia, name='crear_noticia'),
    path('noticia/<int:id>/', views.detalle_noticia, name='detalle_noticia'),
    path('noticia/<int:id>/editar/', views.editar_noticia, name='editar_noticia'),
    path('noticia/<int:id>/eliminar/', views.eliminar_noticia, name='eliminar_noticia'),

    # Archivo histórico (ediciones)
    path('ediciones/', views.archivo_ediciones, name='archivo_ediciones'),
    path('edicion/<int:id>/', views.detalle_edicion, name='detalle_edicion'),

    # Filtro por categoría
    path('categoria/<int:categoria_id>/', views.noticias_por_categoria, name='noticias_por_categoria'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='noticias/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    # Búsqueda por fecha exacta (calendario)
    path('archivo/fecha/', views.archivo_por_dia, name='archivo_por_dia'),                 # /archivo/fecha/?d=YYYY-MM-DD
    path('archivo/<int:year>/<int:month>/<int:day>/', views.archivo_por_dia, name='archivo_por_dia_ymd'),  # /archivo/2025/10/13/

]

# Servir archivos de media en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
