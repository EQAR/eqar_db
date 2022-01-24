from django.db import models
from django.conf import settings
from django.contrib import auth
from uni_db.fields import EnumField

import uuid

class RawQuery(models.Model):
    """
    RawQuery is a simple SQL query
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    description = models.CharField("Description", max_length=255)
    sql = models.TextField("SQL code")
    is_shared = models.BooleanField("Shared", default=False)
    underlying_table = models.CharField("Underlying table", max_length=255, blank=True, null=True)
    owner = models.ForeignKey(auth.models.User, on_delete=models.RESTRICT, verbose_name="Owned by")

    def __str__(self):
        return(self.description)

    class Meta:
        db_table = '_queries'
        verbose_name = "Raw query"
        verbose_name_plural = "Raw queries"
        ordering = [ 'description' ]

