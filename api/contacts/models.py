from django.db import models
from uni_db.fields import EnumField

"""
Contacts: basic models for organisations, persons, etc.
"""

class Role(models.Model):
    id = models.IntegerField("Role ID", primary_key=True, db_column='rid')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return(self.description)

    class Meta:
        db_table = 'role'
        verbose_name = 'organisation type'
        ordering = [ 'id' ]


class Country(models.Model):
    iso3 = models.CharField("ISO 3166-1 alpha-3 code", primary_key=True, max_length=3)
    iso2 = models.CharField("ISO 3166-1 alpha-2 code", unique=True, max_length=2, blank=True, null=True)
    name = models.CharField("name (English)", max_length=255, blank=True, null=True)
    name_local = models.CharField("name (local language)", max_length=255, blank=True, null=True)
    longname = models.CharField("long name (English)", max_length=255, blank=True, null=True)
    longname_local = models.CharField("long name (local language)", max_length=255, blank=True, null=True)
    tableau_name = models.CharField("name (for Tableau)", max_length=255, blank=True, null=True)
    infogram_name = models.CharField("name (for Infogram)", max_length=255, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    tldomain = models.CharField("top-level domain", max_length=2, blank=True, null=True)
    phone_prefix = models.CharField(max_length=5, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    ehea = models.BooleanField("EHEA member", default=False)
    eu = models.BooleanField("EU member", default=False)
    eter = models.BooleanField("covered by ETER", default=False)
    typo3boxdata = models.IntegerField("Typo3 data", blank=True, null=True)

    def __str__(self):
        return('{} ({})'.format(self.name, self.iso2))

    class Meta:
        db_table = 'country'
        verbose_name_plural = "countries"
        ordering = [ 'name' ]


class Contact(models.Model):
    id = models.AutoField("Contact ID", primary_key=True, db_column='cid')
    firstName = models.CharField("first name", db_column='firstName', max_length=255, blank=True, null=True)
    lastName = models.CharField("last name", db_column='lastName', max_length=255, blank=True, null=True)
    person = models.CharField("full name", max_length=255, blank=True, null=True, editable=False)
    nameEmail = models.CharField("label", db_column='nameEmail', blank=True, null=True, max_length=255, editable=False)
    email = models.EmailField("email address", unique=True, max_length=255, blank=True, null=True)
    phone = models.CharField("phone (landline)", max_length=255, blank=True, null=True)
    mobile = models.CharField("phone (mobile)", max_length=255, blank=True, null=True)
    brussels = models.BooleanField("Brussels-based", default=False)
    postal = models.BooleanField("receive paper mail", default=False)
    addressExtension = models.CharField("address extension", db_column='addressExtension', max_length=255, blank=True, null=True)
    address1 = models.CharField(max_length=255, blank=True, null=True, help_text='Insert only if different from organisation!')
    address2 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country', to_field='iso2', blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)
    organisation = models.ManyToManyField('Organisation', through='ContactOrganisation')

    def save(self, *args, **kwargs):
        # auto-generate person
        self.person = \
            '{} {}'.format(self.firstName, self.lastName) if self.firstName and self.lastName \
            else self.firstName \
            or self.lastName \
            or 'NN'
        # auto-generate nameEmail
        self.nameEmail = str(self)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.email:
            return '{} <{}>'.format(self.person or 'NN', self.email)
        elif self.phone:
            return '{} <tel:{}>'.format(self.person or 'NN', self.phone)
        else:
            return '{} [no details]'.format(self.person or 'NN')

    class Meta:
        db_table = 'contact'
        ordering = [ 'lastName', 'firstName' ]
        verbose_name = 'person'


class Organisation(models.Model):
    id = models.AutoField("Organisation ID", primary_key=True, db_column='oid')
    longname = models.CharField("name", max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField("display name", editable=False, blank=True, null=True, max_length=255)
    alt_name = models.CharField("display name (alternate)", editable=False, blank=True, null=True, max_length=255)
    role = models.ForeignKey('Role', models.DO_NOTHING, db_column='role')
    address1 = models.CharField("Address", max_length=255, blank=True, null=True)
    address2 = models.CharField("Address (2)", max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country', to_field='iso2', blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return(f'{self.acronym} - {self.longname}' if self.acronym and self.longname else self.longname or self.acronym)

    def save(self, *args, **kwargs):
        # auto-generate name
        self.name = str(self)
        # auto-generate alt_name
        self.alt_name = f'{self.longname} ({self.acronym})' if self.acronym and self.longname else self.longname or self.acronym
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'organisation'
        ordering = [ 'longname' ]


class ContactOrganisation(models.Model):
    id = models.AutoField("ID", primary_key=True, db_column='coid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, db_column='oid')
    sendOfficial = models.BooleanField("official emails?", default=False, db_column='sendOfficial')
    sendDeqar = models.BooleanField("DEQAR emails?", default=False, db_column='sendDeqar')
    sendInvoice = models.BooleanField("invoice emails?", default=False, db_column='sendInvoice')
    function = models.CharField(max_length=255, blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return('{} <-> {}'.format(self.contact, self.organisation))

    class Meta:
        db_table = 'contact_organisation'
        unique_together = (('organisation', 'contact'),)
        ordering = [ 'function' ]
        verbose_name = 'contact person'


class OctopusAccount(models.Model):
    id = models.AutoField("ID", primary_key=True, db_column='oaid')
    octopusId = models.IntegerField("Octopus relation ID", db_column='octopusId', unique=True)
    name = models.CharField(editable=False, blank=True, max_length=255, null=True)
    organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE, db_column='oid')
    cid = models.ForeignKey(Contact, models.DO_NOTHING, db_column='cid', blank=True, null=True, verbose_name="invoice contact")
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name="invoice contact (manual)")
    client = models.BooleanField(default=False)
    supplier = models.BooleanField(default=False)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return(str(self.organisation))

    def save(self, *args, **kwargs):
        # auto-generate name
        self.name = str(self)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'octopusAccount'
        verbose_name = 'financial account'


class DeqarConnectPartner(models.Model):
    TYPE_CHOICES = [
        ('Coordinator', 'Coordinator'   ),
        ('QAA',         'QAA'           ),
        ('ENIC-NARIC',  'ENIC-NARIC'    ),
        ('Associate',   'Associate'     ),
        ('Expert',      'Expert'        ),
    ]

    id = models.AutoField("Partner ID", primary_key=True, db_column='pid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid')
    pic = models.IntegerField("EU PIC", blank=True, null=True)
    type = EnumField("role", choices=TYPE_CHOICES)
    contact_technical = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='contact_technical', blank=True, null=True, related_name='deqar_connect_tech')
    contact_admin = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='contact_admin', blank=True, null=True, related_name='deqar_connect_admin')
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return(f'P{self.id:02d} {self.organisation}')

    class Meta:
        db_table = 'deqarConnectPartner'
        ordering = [ 'id' ]
        verbose_name = 'DEQAR CONNECT partner'


class DeqarPartner(models.Model):
    TYPE_CHOICES = [
        ('Coordinator',         'Coordinator'           ),
        ('Stakeholder Partner', 'Stakeholder Partner'   ),
        ('QAA Partner',         'QAA Partner'           ),
        ('Research Centre',     'Research Centre'       ),
        ('Associate Partner',   'Associate Partner'     ),
    ]

    id = models.AutoField("Partner ID", primary_key=True, db_column='pid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid')
    pic = models.IntegerField("EU PIC", blank=True, null=True)
    pic_name = models.CharField("official name (PIC)", max_length=255, blank=True, null=True)
    type = EnumField("role", choices=TYPE_CHOICES)
    manager = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='manager', blank=True, null=True, related_name='deqar1_manager')
    technician = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='technician', blank=True, null=True, related_name='deqar1_tech')
    signatory = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='signatory', blank=True, null=True, related_name='deqar1_sign')
    signatory_name = models.CharField(max_length=255, blank=True, null=True)
    expenditure = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    max_contrib = models.DecimalField("max. EU grant", max_digits=8, decimal_places=2, blank=True, null=True)
    prog_report_expected = models.DateField("progress report expected by", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return(f'P{self.id:02d} {self.organisation}')

    class Meta:
        db_table = 'deqarPartner'
        ordering = [ 'id' ]
        verbose_name = 'DEQAR project partner'

