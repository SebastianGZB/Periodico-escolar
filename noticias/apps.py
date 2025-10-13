# noticias/apps.py
from django.apps import AppConfig

class NoticiasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'noticias'

    def ready(self):
        # Registrar hook post_migrate para sembrar categorías por defecto
        from django.db.models.signals import post_migrate
        from django.apps import apps as django_apps
        from django.utils.text import slugify

        def ensure_default_categories(sender, **kwargs):
            Categoria = django_apps.get_model('noticias', 'Categoria')
            nombres = ["Deportes", "Entretenimiento", "Escolar", "Ciencia y Tecnología"]
            for nombre in nombres:
                obj, created = Categoria.objects.get_or_create(nombre=nombre)
                # Si tu modelo tiene campo 'slug', lo rellenamos si está vacío
                if hasattr(obj, 'slug'):
                    if not getattr(obj, 'slug', None):
                        obj.slug = slugify(nombre)
                        try:
                            obj.save(update_fields=['slug'])
                        except Exception:
                            obj.save()

        # Conectar la señal (weak=False para que no se “recolecte basura”)
        post_migrate.connect(ensure_default_categories, sender=self, weak=False)
