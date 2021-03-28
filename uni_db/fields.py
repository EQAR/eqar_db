from django.db import models, NotSupportedError
from django.core.exceptions import ImproperlyConfigured

class EnumField(models.Field):

    """
    A field class that maps to MySQL/MariaDB's ENUM type.

    Usage:

    class ABC(models.Model):
        a = EnumField(choices=[('code-a','Label A'),...])

    """

    def __init__(self, *args, **kwargs):
        if 'choices' not in kwargs:
            raise ImproperlyConfigured('A list of choices is required.')
        if not isinstance(kwargs['choices'], list):
            raise ImproperlyConfigured('Wrong data type: choices must be a list.')
        if len(kwargs['choices']) < 1:
            raise ImproperlyConfigured('There must be at least one choice.')

        self.values = [ i[0] for i in kwargs['choices'] ]
        if not all(isinstance(v, str) for v in self.values):
            raise ImproperlyConfigured("MySQL ENUM values should be strings")

        if 'default' not in kwargs and ( ('null' not in kwargs) or not kwargs['null']):
            """
                If default is not set and field is not nullable, we need a default.

                This corresponds to MariaDB behaviour, which is to use the first
                option as default value.
            """
            kwargs['default'] = self.values[0]

        super(EnumField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] != 'django.db.backends.mysql':
            raise NotSupportedError('EnumField is only supported for MySQL/MariaDB')
        return "enum({0})".format( ','.join("'{}'".format(v) for v in self.values) )

