from django.db import models
from contacts.models import Organisation, OctopusAccount
from eqar_db.custom_fields import EnumField

"""
Members: EQAR member organisations
"""

class Member(models.Model):
    CAT_CHOICES = [
        ('FOU', 'Founding'),
        ('SOP', 'Social Partner'),
        ('GOV', 'Governmental'),
        ('OBS', 'Observer'),
    ]

    id = models.AutoField(primary_key=True, db_column='mid')
    cat = EnumField(choices=CAT_CHOICES)
    organisation = models.OneToOneField(Organisation, models.RESTRICT, db_column='oid')
    name = models.CharField(max_length=255, blank=True, null=True)
    form_date = models.DateField(db_column='formDate', blank=True, null=True)  # Field name made lowercase.
    signatory = models.CharField(max_length=255, blank=True, null=True)
    function = models.CharField(max_length=255, blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('{}: {}'.format(self.name, self.organisation))

    class Meta:
        db_table = 'member'
        ordering = [ 'cat', 'name' ]


class Invoice(models.Model):
    id = models.AutoField(primary_key=True, db_column='iid')
    member = models.ForeignKey(Member, models.CASCADE, db_column='mid')
    account = models.OneToOneField(OctopusAccount, models.RESTRICT, db_column='oaid')
    fee = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('{}: {}€ @ {} '.format(self.member.name, self.fee, self.account))

    class Meta:
        db_table = 'invoice'


