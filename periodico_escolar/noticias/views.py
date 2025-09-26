from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import Noticia, Reaccion, Edicion
from .forms import NoticiaForm, ComentarioForm, ReaccionForm, RegistroForm


# -------------------------------
# Archivo histórico de ediciones
# -------------------------------
def archivo_ediciones(request):
    ediciones = Edicion.objects.all().order_by('-fecha')
    return render(request, 'noticias/archivo_ediciones.html', {'ediciones': ediciones})

def detalle_edicion(request, id):
    edicion = get_object_or_404(Edicion, id=id)
    noticias = edicion.noticias.all().order_by('-fecha')
    return render(request, 'noticias/detalle_edicion.html', {'edicion': edicion, 'noticias': noticias})

# -------------------------------
# Inicio
# -------------------------------
def inicio(request):
    noticias = Noticia.objects.all().order_by('-fecha')
    return render(request, 'noticias/inicio.html', {'noticias': noticias})

# -------------------------------
# Detalle de noticia
# -------------------------------
def detalle_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    likes = noticia.reaccion_set.filter(tipo='like').count()
    dislikes = noticia.reaccion_set.filter(tipo='dislike').count()
    comentarios = noticia.comentario_set.all().order_by('-fecha')

    # Obtener última edición de esta noticia (Edicion mensual original)
    ultima_edicion = noticia.edicion_set.order_by('-fecha').first()

    fecha_edicion = noticia.fecha_edicion

    comentario_form = None
    reaccion_form = None

    if request.user.is_authenticated:
        comentario_form = ComentarioForm()
        reaccion_form = ReaccionForm()

        if request.method == 'POST':
            if 'comentario_submit' in request.POST:
                comentario_form = ComentarioForm(request.POST)
                if comentario_form.is_valid():
                    comentario = comentario_form.save(commit=False)
                    comentario.autor = request.user
                    comentario.noticia = noticia
                    comentario.save()
                    return redirect('detalle_noticia', id=id)

            elif 'reaccion_submit' in request.POST:
                reaccion_form = ReaccionForm(request.POST)
                if reaccion_form.is_valid():
                    reaccion, created = Reaccion.objects.get_or_create(
                        usuario=request.user,
                        noticia=noticia,
                        defaults={'tipo': reaccion_form.cleaned_data['tipo']}
                    )
                    if not created:
                        reaccion.tipo = reaccion_form.cleaned_data['tipo']
                        reaccion.save()
                    return redirect('detalle_noticia', id=id)

    return render(request, 'noticias/detalle.html', {
        'noticia': noticia,
        'likes': likes,
        'dislikes': dislikes,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
        'reaccion_form': reaccion_form,
        'ultima_edicion': ultima_edicion,
        'fecha_edicion': fecha_edicion 
    })

# -------------------------------
# Crear noticia (solo redactor/editor)
# -------------------------------
@login_required
def crear_noticia(request):
    if not (request.user.is_redactor() or request.user.is_editor()):
        return redirect('inicio')  # o HttpResponseForbidden("No tienes permisos")

    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.autor = request.user
            noticia.save()

            # Usa la fecha de creación real
            now = noticia.fecha

            # Edición del mes de creación
            start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_month = start_month.replace(year=now.year + 1, month=1)
            else:
                end_month = start_month.replace(month=now.month + 1)

            edicion = Edicion.objects.filter(fecha__gte=start_month, fecha__lt=end_month).first()
            if not edicion:
                # Ojo: %B depende de locale; si ves el mes en inglés, mejor formatear en template
                edicion = Edicion.objects.create(fecha=now, titulo=f'Edición {now.strftime("%B %Y")}')

            edicion.noticias.add(noticia)
            return redirect('inicio')
    else:
        form = NoticiaForm()

    return render(request, 'noticias/crear.html', {'form': form})

# -------------------------------
# Editar noticia (autor o editor)
# -------------------------------
@login_required
def editar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    # autor o editor
    if not (request.user == noticia.autor or request.user.is_editor()):
        return redirect('detalle_noticia', id=id)  # o HttpResponseForbidden("No tienes permisos")

    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()  # setea fecha_edicion via modelo
            return redirect('detalle_noticia', id=id)
    else:
        form = NoticiaForm(instance=noticia)

    return render(request, 'noticias/editar.html', {'form': form, 'noticia': noticia})

# -------------------------------
# Registro de usuarios
# -------------------------------
def signup(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not getattr(user, 'role', None):
                user.role = 'lector'
            user.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'noticias/signup.html', {'form': form})

# -------------------------------
# Eliminar Noticia
# -------------------------------
@login_required
def eliminar_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)
    if not (request.user == noticia.autor or request.user.is_editor()):
        return HttpResponseForbidden("No tienes permisos para eliminar esta noticia.")

    if request.method == 'POST':
        titulo = noticia.titulo
        noticia.delete()
        messages.success(request, f'Noticia "{titulo}" eliminada.')
        return redirect('inicio')

    return render(request, 'noticias/confirmar_eliminar.html', {'noticia': noticia})

# -------------------------------
# Permiso Edicion
# -------------------------------
def puede_editar_noticia(user, noticia):
    if not user.is_authenticated:
        return False
    if user == noticia.autor or user.is_editor():
        return True
    # ¿colaborador con permiso?
    from .models import ColaboracionNoticia
    return ColaboracionNoticia.objects.filter(usuario=user, noticia=noticia, puede_editar=True).exists()