from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    def validate_username(value):
        """
        Недопустимо использовать имя пользователя me.
        """
        if value == 'me':
            raise ValidationError(
                ('Недопустимый логин "me"'),
            )

    username = models.CharField(
        'Логин',
        validators=(UnicodeUsernameValidator(), validate_username,),
        max_length=150,
        unique=True,
        null=False,
    )
    email = models.EmailField(
        "Электронная почта",
        help_text=(
            'Required. 150 characters or fewer.\
                  Letters, digits and @/./+/-/_ only.'),
        max_length=254,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        null=False,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'last_name', 'first_name', 'username']
