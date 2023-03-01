import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, first_name, last_name, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.password = make_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_mentor", False)
        return self._create_user(first_name, last_name, email, password, **extra_fields)

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(first_name, last_name, email, password, **extra_fields)


class CustomUser(AbstractUser):
    class Experience(models.TextChoices):
        self = 'Experience.self', _('self')
        professional = 'Experience.professional', _('professional')
        online = 'Experience.online', _('online')
        other = 'Experience.other', _('other')

    class Types(models.TextChoices):
        user = 'Types.user', _('user')
        mentor = 'Types.mentor', _('mentor')

    class Audience(models.TextChoices):
        no = 'Audience.no', _('no')
        small = 'Audience.small', _('small')
        medium = 'Audience.medium', _('medium')

    username = None
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=40, choices=Types.choices, default=Types.user)
    experience = models.CharField(max_length=40, choices=Experience.choices, null=True, blank=True)
    audience = models.CharField(max_length=40, choices=Audience.choices, null=True, blank=True)

    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def create_activation_code(self):
        self.activation_code = str(uuid.uuid4())
