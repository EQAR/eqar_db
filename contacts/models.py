from django.db import models
from eqar_db.custom_fields import EnumField

"""
Contacts: basic models for organisations, persons, etc.
"""

class Language(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    language = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return(self.language)

    class Meta:
        db_table = 'language'
        ordering = [ 'language' ]


class Role(models.Model):
    id = models.IntegerField(primary_key=True, db_column='rid')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return(self.description)

    class Meta:
        db_table = 'role'
        ordering = [ 'id' ]


class Country(models.Model):
    iso3 = models.CharField(primary_key=True, max_length=3)
    iso2 = models.CharField(unique=True, max_length=2, blank=True, null=True)
    longname = models.CharField(max_length=255, blank=True, null=True)
    longname_local = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    name_local = models.CharField(max_length=255, blank=True, null=True)
    tableau_name = models.CharField(max_length=255, blank=True, null=True)
    infogram_name = models.CharField(max_length=255, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    tldomain = models.CharField(max_length=2, blank=True, null=True)
    phone_prefix = models.CharField(max_length=5, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    ehea = models.IntegerField()
    eu = models.IntegerField()
    eter = models.IntegerField()
    typo3boxdata = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return('{} ({})'.format(self.name, self.iso2))

    class Meta:
        db_table = 'country'
        ordering = [ 'name' ]


class Contact(models.Model):
    id = models.AutoField(primary_key=True, db_column='cid')
    firstname = models.CharField(db_column='firstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    #person = models.CharField(max_length=255, editable=False)
    #name_email = models.CharField(db_column='nameEmail', max_length=255, editable=False)  # Field name made lowercase.
    email = models.EmailField(unique=True, max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    brussels = models.BooleanField(default=False)
    postal = models.BooleanField(default=False)
    pref_lang = models.ForeignKey(Language, on_delete=models.RESTRICT, db_column='prefLang', default='en')  # Field name made lowercase.
    address_extension = models.CharField(db_column='addressExtension', max_length=255, blank=True, null=True)  # Field name made lowercase.
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country', to_field='iso2', blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)
    organisation = models.ManyToManyField('Organisation', through='ContactOrganisation')

    @property
    def person(self):
        return '{} {}'.format(self.firstname, self.lastname) if self.firstname and self.lastname else self.firstname or self.lastname or 'NN'

    @property
    def fullname(self):
        return self.person

    def __str__(self):
        if self.email:
            return '{} <{}>'.format(self.person, self.email)
        elif self.phone:
            return '{} <tel:{}>'.format(self.person, self.phone)
        else:
            return '{} [no details]'.format(self.person)

    class Meta:
        db_table = 'contact'
        ordering = [ 'lastname', 'firstname' ]


class Organisation(models.Model):
    id = models.AutoField(primary_key=True, db_column='oid')
    longname = models.CharField(max_length=255, blank=True, null=True)
    acronym = models.CharField(max_length=15, blank=True, null=True)
    #name = models.CharField(max_length=255, editable=False)
    #alt_name = models.CharField(max_length=255, editable=False)
    role = models.ForeignKey('Role', models.DO_NOTHING, db_column='role')
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country', to_field='iso2', blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('{} ({})'.format(self.longname, self.acronym) if self.acronym and self.longname else self.longname or self.acronym)

    class Meta:
        db_table = 'organisation'
        ordering = [ 'longname' ]


class ContactOrganisation(models.Model):
    id = models.AutoField(primary_key=True, db_column='coid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, db_column='oid')
    sendofficial = models.BooleanField(default=False, db_column='sendOfficial')  # Field name made lowercase.
    senddeqar = models.BooleanField(default=False, db_column='sendDeqar')  # Field name made lowercase.
    sendinvoice = models.BooleanField(default=False, db_column='sendInvoice')  # Field name made lowercase.
    function = models.CharField(max_length=255, blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('{} <-> {}'.format(self.contact, self.organisation))

    class Meta:
        db_table = 'contact_organisation'
        unique_together = (('organisation', 'contact'),)
        ordering = [ 'function' ]


class OctopusAccount(models.Model):
    id = models.AutoField(primary_key=True, db_column='oaid')
    octopus_id = models.IntegerField(db_column='octopusId', unique=True)  # Field name made lowercase.
    organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE, db_column='oid')
    #name = models.CharField(max_length=255, blank=True, null=True)
    cid = models.ForeignKey(Contact, models.DO_NOTHING, db_column='cid', blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    client = models.BooleanField(default=False)
    supplier = models.BooleanField(default=False)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return(str(self.organisation))

    class Meta:
        db_table = 'octopusAccount'


class DeqarConnectPartner(models.Model):
    TYPE_CHOICES = [
        ('Coordinator', 'Coordinator'   ),
        ('QAA',         'QAA'           ),
        ('ENIC-NARIC',  'ENIC-NARIC'    ),
        ('Associate',   'Associate'     ),
        ('Expert',      'Expert'        ),
    ]

    id = models.AutoField(primary_key=True, db_column='pid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid')
    pic = models.IntegerField(blank=True, null=True)
    type = EnumField(choices=TYPE_CHOICES)
    contact_technical = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='contact_technical', blank=True, null=True, related_name='deqar_connect_tech')
    contact_admin = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='contact_admin', blank=True, null=True, related_name='deqar_connect_admin')
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('P{} {}'.format(self.id, self.organisation))

    class Meta:
        db_table = 'deqarConnectPartner'
        ordering = [ 'id' ]


class DeqarPartner(models.Model):
    TYPE_CHOICES = [
        ('Coordinator',         'Coordinator'           ),
        ('Stakeholder Partner', 'Stakeholder Partner'   ),
        ('QAA Partner',         'QAA Partner'           ),
        ('Research Centre',     'Research Centre'       ),
        ('Associate Partner',   'Associate Partner'     ),
    ]

    id = models.AutoField(primary_key=True, db_column='pid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid')
    pic = models.IntegerField(blank=True, null=True)
    pic_name = models.CharField(max_length=255, blank=True, null=True)
    type = EnumField(choices=TYPE_CHOICES)
    manager = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='manager', blank=True, null=True, related_name='deqar1_manager')
    technician = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='technician', blank=True, null=True, related_name='deqar1_tech')
    signatory = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='signatory', blank=True, null=True, related_name='deqar1_sign')
    signatory_name = models.CharField(max_length=255, blank=True, null=True)
    expenditure = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    max_contrib = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    prog_report_expected = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('P{} {}'.format(self.id, self.organisation))

    class Meta:
        db_table = 'deqarPartner'
        ordering = [ 'id' ]


