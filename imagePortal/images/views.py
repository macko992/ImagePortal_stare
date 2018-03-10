from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .forms import UploadImageForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
import redis
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


@login_required
def image_upload(request):
    if request.method == 'POST':
        upload_form = UploadImageForm(request.POST, request.FILES)
        if ulpoad_form.is_valid():
            new_item=upload_form.save(commit=False)
            new_item.image=request.FILES['image']
            new_item.save()
            messages.success(request, 'Obraz został dodany.')
            return redirect('new_item.get_absolute_url()')
    else:
        upload_form=UploadImageForm()
    return render(request, 'images/image/upload_image.html',
                  {'upload_form': upload_form, 'section': 'images' })


@login_required
def image_create(request):
    if request.method == 'POST':
        # Formularz został wysłany.
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Dane formularza są prawidłowe.
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            # Przypisanie bieżącego użytkownika do elementu.
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'Added Image', new_item)
            messages.success(request, 'Obraz został dodany.')
            # Przekierowanie do widoku szczegółowego
            # dla nowo utworzonego elementu.
            return redirect(new_item.get_absolute_url())
    else:
        # Utworzenie formularza na podstawie danych
        # i  dostarczonych przez bookmarklet w żądaniu GET.
        form = ImageCreateForm(data=request.GET)

    return render(request,
                  'images/image/create.html',
                  {'section': 'images',
                   'form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # Inkrementacja o 1 całkowitej liczby wyświetleń danego obrazu.
    total_views = r.incr('image:{}:views'.format(image.id))
    # Inkrementacja o 1 rankingu danego obrazu.
    r.zincrby('image_ranking', image.id, 1)
    return render(request, 'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})



login_required
def image_ranking(request):
    # Pobranie słownika rankingu obrazów.
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # Pobranie najczęściej wyświetlanych obrazów.
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html',
                  {'section': 'images',
                   'most_viewed': most_viewed})



@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'Liked', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ok'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 18)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:

        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():

            return HttpResponse('')

        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images',
                       'images': images})
    return render(request,
                  'images/image/list.html',
                   {'section': 'images',
                    'images': images})
