from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        also create a profile for this user
        """
        first_name = extra_fields.pop('first_name', None)
        last_name = extra_fields.pop('last_name', None)
        birthdate = extra_fields.pop('birthdate', None)
        my_user = super()._create_user(username, email, password, **extra_fields)
        MyProfile(my_user=my_user, first_name=first_name, last_name=last_name, birthdate=birthdate).save()
        return my_user

    def get_or_create_user(self, username='test', password='test', **extra_fields):
        try:
            return MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return MyUser.objects.create_user(username=username, password=password, **extra_fields)


class MyUser(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    objects = MyUserManager()
    first_name = None
    last_name = None

    def __str__(self):
        return f'{self.username}'


class MyImage(models.Model):
    my_profile = models.ForeignKey('MyProfile', on_delete=models.CASCADE, related_name='my_images')
    image = models.ImageField()


class MyProfile(models.Model):
    my_user = models.OneToOneField('MyUser', on_delete=models.CASCADE, related_name='my_profile')
    first_name = models.CharField( max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    birthdate = models.DateField(blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.my_user}'
