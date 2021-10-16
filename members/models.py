from django.db import models
from contacts.models import Organisation, OctopusAccount
from uni_db.fields import EnumField


class Member(models.Model):

    """
    An EQAR member organisation
    """

    CAT_CHOICES = [
        ('FOU', 'Founding'),
        ('SOP', 'Social Partner'),
        ('GOV', 'Governmental'),
        ('OBS', 'Observer'),
    ]

    id = models.AutoField("member ID", primary_key=True, db_column='mid')
    cat = EnumField("category", choices=CAT_CHOICES)
    name = models.CharField("member", max_length=255, blank=True, null=True)
    organisation = models.OneToOneField(Organisation, models.RESTRICT, db_column='oid')
    form_date = models.DateField("form date", db_column='formDate', blank=True, null=True)  # Field name made lowercase.
    signatory = models.CharField("form signatory", max_length=255, blank=True, null=True)
    function = models.CharField("form signatory's function", max_length=255, blank=True, null=True)
    votes = models.IntegerField("votes", blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return('{}: {}'.format(self.name, self.organisation))

    class Meta:
        db_table = 'member'
        verbose_name = "EQAR Member"
        ordering = [ 'cat', 'name' ]


class Invoice(models.Model):

    """
    Invoice info for membership fees
    """

    id = models.AutoField("invoice ID", primary_key=True, db_column='iid')
    member = models.ForeignKey(Member, models.CASCADE, db_column='mid', verbose_name="Member")
    account = models.OneToOneField(OctopusAccount, models.RESTRICT, db_column='oaid', verbose_name="financial account")
    fee = models.DecimalField("membership fee", max_digits=7, decimal_places=2, blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return('{}: {}€ @ {} '.format(self.member.name, self.fee, self.account))

    class Meta:
        db_table = 'invoice'


