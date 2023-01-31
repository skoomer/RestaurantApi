from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """add user field  to admin dashboard"""
    list_display = ("id", "email", "first_name", "last_name")


admin.site.register(User, UserAdmin)
