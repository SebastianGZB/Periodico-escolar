from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import datetime, date
from django.utils.timezone import make_aware
from django.core.exceptions import ValidationError
from .models import Noticia, Reaccion, Edicion, Categoria
from .forms import NoticiaForm, ComentarioForm, ReaccionForm, RegistroForm



def archivo_por_dia(request, year=None, month=None, day=None):
    # 1) Si vienen en la URL /archivo/2025/10/13/
    selected_date = None
    if year and month and day:
        try:
            selected_date = date(int(year), int(month), int(day))
        except ValueError:
            selected_date = None

    # 2) O si vienen por querystring en /archivo/fecha/?d=YYYY-MM-DD
    if not selected_date:
        d = request.GET.get('d')
        if d:
            try:
                selected_date = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                selected_date = None

    noticias = []
    error = None

    if selected_date:
        # Asumimos Noticia.fecha es DateTimeField; filtramos por la parte de fecha
        noticias = Noticia.objects.filter(fecha__date=selected_date).order_by('-fecha')
        if not noticias:
            error = "No hay noticias en la fecha seleccionada."
    else:
        error = "Selecciona una fecha para buscar noticias."

    # Para mostrar un valor por defecto en el input
    initial_value = selected_date.isoformat() if selected_date else ""

    return render(request, 'noticias/archivo_por_dia.html', {
        'noticias': noticias,
        'error': error,
        'selected_date': selected_date,
        'initial_value': initial_value,
    })

# -------------------------------
# Filtro por categoría
# -------------------------------
def noticias_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    noticias = Noticia.objects.filter(categoria=categoria).order_by('-fecha')  # sin 'estado'
    return render(request, 'noticias/noticias_por_categoria.html', {
        'categoria': categoria,
        'noticias': noticias
    })


# -------------------------------
# Archivo histórico de ediciones
# -------------------------------
def archivo_ediciones(request):
    """
    Muestra el listado de ediciones y, opcionalmente, resultados por un día exacto
    si se recibe ?d=YYYY-MM-DD en la querystring.
    """
    # Ediciones (para la grilla principal)
    ediciones = Edicion.objects.all().order_by('-fecha')

    # Soporte de búsqueda por día, integrada en esta misma página
    selected_date = None
    noticias_por_dia = []
    error_fecha = None

    d = request.GET.get('d')
    if d:
        try:
            # intenta parsear YYYY-MM-DD
            selected_date = datetime.strptime(d, "%Y-%m-%d").date()
            # filtra por día exacto (Noticia.fecha es DateTimeField)
            noticias_por_dia = Noticia.objects.filter(fecha__date=selected_date).order_by('-fecha')
            if not noticias_por_dia:
                error_fecha = "No hay noticias en la fecha seleccionada."
        except ValueError:
            error_fecha = "Fecha inválida. Usa el formato YYYY-MM-DD."

    context = {
        'ediciones': ediciones,
        'selected_date': selected_date,
        'noticias_por_dia': noticias_por_dia,
        'error_fecha': error_fecha,
        'initial_value': selected_date.isoformat() if selected_date else "",
    }
    return render(request, 'noticias/archivo_ediciones.html', context)


def detalle_edicion(request, id):
    edicion = get_object_or_404(Edicion, id=id)
    noticias = edicion.noticias.all().order_by('-fecha')
    return render(request, 'noticias/detalle_edicion.html', {'edicion': edicion, 'noticias': noticias})


# -------------------------------
# Inicio
# -------------------------------
def inicio(request):
    noticias = Noticia.objects.all().order_by('-fecha')  # sin 'estado'
    categorias = Categoria.objects.all()
    return render(request, 'noticias/inicio.html', {
        'noticias': noticias,
        'categorias': categorias
    })


# -------------------------------
# Detalle de noticia
# -------------------------------
def detalle_noticia(request, id):
    noticia = get_object_or_404(Noticia, id=id)

    likes = noticia.reaccion_set.filter(tipo='like').count()
    dislikes = noticia.reaccion_set.filter(tipo='dislike').count()
    comentarios = noticia.comentario_set.all().order_by('-fecha')

    # Última edición asociada a esta noticia
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
                # %B depende de locale; puedes formatear el mes en el template si prefieres
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
        messages.success(request, f'Noticia \"{titulo}\" eliminada.')
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
