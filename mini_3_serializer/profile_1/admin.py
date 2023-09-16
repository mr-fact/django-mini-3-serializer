from django.contrib import admin

from profile_1.models import MyUser, MyProfile


@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(MyProfile)
class UserAdmin(admin.ModelAdmin):
    pass
