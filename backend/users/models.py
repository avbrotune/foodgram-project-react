from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import validate_username


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name', 'username']

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
            'Обязательное поле. Не более 150 символов.\
                  Только латинские буквы, цифры и симовлы @/./+/-/_.'),
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

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['last_name', ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
