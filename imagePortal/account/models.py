from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/%Y/%m/%d',
                              blank=True)
    def __str__(self):
        return 'User Profile {}.'.format(self.user.username)

class Contact(models.Model):
    #klucz dla user'a, który tworzy związek
    user_from = models.ForeignKey(User, related_name='rel_from_set')
    #klucz dla usera, który jest obserwowany
    user_to = models.ForeignKey(User, related_name='rel_to_set')
    #przechowuje datę i czas, kiedy został stworzony związek
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)

#Dynamiczne dodanie kolumny do modelu User
User.add_to_class('following', models.ManyToManyField('self', through=Contact,
                                                      related_name='followers',
                                                      symmetrical=False))
# add_to_class - dynamiczne dodanie kolumny (niby nie zalecane)
#symetrical - związek symetryczny ( tworzymy zwiazek nie symetryczny )
