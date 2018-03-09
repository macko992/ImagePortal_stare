from django.contrib import admin
from .models import Profile

class ProfieAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'photo']

admin .site.register(Profile, ProfieAdmin)
