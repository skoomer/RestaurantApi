from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """User manager"""

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Abstract user model."""

    def upload_to(instance, filename):
        return 'images/user_{0}/{1}'.format(instance.id, filename)

    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
        unique=True,
    )
    username = None
    first_name = models.CharField(max_length=30, blank=True, verbose_name="first name")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="last name")
    is_active = models.BooleanField(default=True, verbose_name="active")
    is_admin = models.BooleanField(default=False, verbose_name="admin")
    avatar = models.ImageField(upload_to=upload_to, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self):
        """return email"""
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?
        Returns True if the user has the specified permission, where perm is in the format
         "<app label>.<permission codename>"
        (see permissions). If User.is_active and is_superuser are both True,
         this method always returns True."""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?.
        Returns True if the user has any permissions in the given package (the Django app label).
        If User.is_active and is_superuser are both True, this method always returns True."""
        # Simplest possible answer: All admins are staff
        return self.is_admin
