from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.contrib.auth.models import User
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.utils import create_action
from actions.models import Action



def user_login(request): #powywołaniu tego zostanie utworzony formularz logownia
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid(): #sprawdzenie czy formularz jest prawidłowy
            cd = form.cleaned_data #czyści gdzy np user wprowadzi błędne dane
            user = authenticate(username = cd['username'],
                                password = cd['password'])
            if user is not None:
                if user.is_active: #sprawdza czy user jest juz aktywny
                    login(request, user)
                    return HttpResponse('Authenticated is succesfull') # uwierzytelnianie zakończone sukcesem
                else:
                    return HttpResponse('Account is blocked') #konto jest zablokowane
        else:
            return HttpResponse('Incorrect authentication data') #nieprawidłowe dane uwierzytelniania
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def register(request): #tworzenie rejestracji Usera
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #ponizej tworzymy obiekt nowego user ale nie zapisujemy go jeszcze wazie
            new_user = user_form.save(commit=False)
            #Ustawienie wybranego hasła
            new_user.set_password(user_form.cleaned_data['password']) #czyści gdzy np user wprowadzi błędne dane
            new_user.save()
            profile = Profile.objects.create(user = new_user) #przy reestracji tworzy się juz Profil usera
            create_action = (new_user, 'created account')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def editProfile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance = request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'upgrade completed successfully')
        else:
            messages.error(request, 'There was an error during the upgrade')
    else:
         user_form = UserEditForm(instance=request.user)
         profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/editProfile.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(editProfile)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
                create_action(request.user, 'followers', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})

@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section': 'people',
                   'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                   'user': user})


@login_required
def dashboard(request):
    # Domyślnie wyświetlane są wszystkie akcje.
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # Jeżeli użytkownik obserwuje innych, będzie otrzymywał jedynie
        # informacje o podejmowanych przez nich akcjach.
        actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related('target')
    actions = actions[:10]

    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})
