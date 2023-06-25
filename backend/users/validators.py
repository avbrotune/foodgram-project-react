from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Недопустимо использовать имя пользователя me.
    """
    if value == 'me':
        raise ValidationError(
            ('Недопустимый логин "me"'),
        )
