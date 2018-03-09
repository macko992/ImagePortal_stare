from django import forms
from django.contrib.auth.models import User
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label = 'Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label = 'Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password'] != cd['password2']:
                raise forms.ValidationError('Passwords are not the same') #hasła nie są takie same
            return cd['password2']

class UserEditForm(forms.ModelForm): #pozwala userowi na edycję imie, nazwisko, email( w modelu User)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):  #pozwala na edycję daty urodzin i avatara ( w modlu Profile )
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')
