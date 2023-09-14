from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        also create a profile for this user
        """
        my_user = super()._create_user(username, email, password, **extra_fields)
        MyProfile(my_user=my_user, **extra_fields).save()
        return my_user

    def get_or_create_user(self, username='test', password='test'):
        try:
            return MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            return MyUser.objects.create_user(username=username, password=password)


class MyUser(AbstractUser):
    friends = models.ManyToManyField('self', blank=True, null=True)
    objects = MyUserManager()
    first_name = None
    last_name = None


class MyImage(models.Model):
    my_profile = models.ForeignKey('MyProfile', on_delete=models.CASCADE, related_name='my_images')
    image = models.ImageField()


class MyProfile(models.Model):
    my_user = models.OneToOneField('MyUser', on_delete=models.CASCADE, related_name='my_profile')
    first_name = models.CharField( max_length=255, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    birthdate = models.DateField(blank=True, null=True, default=None)
