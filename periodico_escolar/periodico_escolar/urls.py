from django.contrib import admin
from django.urls import path, include
from noticias import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_noticia, name='crear_noticia'),
    path('noticia/<int:id>/', views.detalle_noticia, name='detalle_noticia'),
    path('noticia/<int:id>/editar/', views.editar_noticia, name='editar_noticia'),
    path('noticia/<int:id>/eliminar/', views.eliminar_noticia, name='eliminar_noticia'),
    path('ediciones/', views.archivo_ediciones, name='archivo_ediciones'),
    path('edicion/<int:id>/', views.detalle_edicion, name='detalle_edicion'),

    path('login/', auth_views.LoginView.as_view(template_name='noticias/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]

# servir media en desarrollo
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)