from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Noticia, Comentario, Reaccion

User = get_user_model()

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'contenido', 'categoria', 'imagen']

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']

class ReaccionForm(forms.ModelForm):
    class Meta:
        model = Reaccion
        fields = ['tipo']

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User                    
        fields = ['username', 'email', 'password1', 'password2']
