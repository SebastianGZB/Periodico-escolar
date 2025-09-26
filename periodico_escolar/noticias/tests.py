from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from noticias.models import User, Categoria, Noticia

class RolesTests(TestCase):
    def setUp(self):
        self.lector = User.objects.create_user(username='lector1', password='123', role='lector')
        self.redactor = User.objects.create_user(username='redactor1', password='123', role='redactor')
        self.editor = User.objects.create_user(username='editor1', password='123', role='editor')
        self.cat = Categoria.objects.create(nombre='General')
        self.noticia_redactor = Noticia.objects.create(
            titulo='N1', contenido='...', categoria=self.cat, autor=self.redactor
        )

    def test_lector_no_puede_crear(self):
        self.client.login(username='lector1', password='123')
        resp = self.client.get(reverse('crear_noticia'))
        self.assertEqual(resp.status_code, 302)  # redirige (o 403 si usas Forbidden)

    def test_redactor_puede_crear(self):
        self.client.login(username='redactor1', password='123')
        resp = self.client.get(reverse('crear_noticia'))
        self.assertEqual(resp.status_code, 200)

    def test_redactor_no_edita_ajeno(self):
        # otro autor
        otro = User.objects.create_user(username='otro', password='123', role='redactor')
        noticia_ajena = Noticia.objects.create(titulo='N2', contenido='...', categoria=self.cat, autor=otro)
        self.client.login(username='redactor1', password='123')
        resp = self.client.get(reverse('editar_noticia', args=[noticia_ajena.id]))
        self.assertEqual(resp.status_code, 302)  # redirige al detalle

    def test_redactor_si_edita_suya(self):
        self.client.login(username='redactor1', password='123')
        resp = self.client.get(reverse('editar_noticia', args=[self.noticia_redactor.id]))
        self.assertEqual(resp.status_code, 200)

    def test_editor_edita_cualquiera(self):
        self.client.login(username='editor1', password='123')
        resp = self.client.get(reverse('editar_noticia', args=[self.noticia_redactor.id]))
        self.assertEqual(resp.status_code, 200)