from django.db import models
from django.template.defaultfilters import slugify

from contacts.models import Organisation, Contact, OctopusAccount, Country, ContactOrganisation
from uni_db.fields import EnumField

"""
Agencies: everything related to registered agencies, applications, etc.
"""

class RegisteredAgency(models.Model):
    T_BASE_URL = 'https://data.deqar.eu/agency/'

    id = models.AutoField('Agency ID', primary_key=True, db_column='rid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid', blank=True, null=True)
    octopusAccount = models.OneToOneField(OctopusAccount, on_delete=models.RESTRICT, db_column='oaid', blank=True, null=True, verbose_name='financial account')
    shortname = models.CharField('Acronym', max_length=255, blank=True, null=True)
    mainContact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='mainContact', blank=True, null=True,
                                        related_name='agency_main', verbose_name='main contact')
    webContact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='webContact', blank=True, null=True,
                                        related_name='agency_web', verbose_name='website contact')
    registered = models.BooleanField(default=False)
    deqarId = models.IntegerField(db_column='deqarId', unique=True, blank=True, null=True, verbose_name='DEQAR ID')
    registerUrl = models.CharField(editable=False, blank=True, db_column='registerUrl', max_length=255, null=True)
    registeredSince = models.DateField(db_column='registeredSince', blank=True, null=True, verbose_name='registered since')
    validUntil = models.DateField(db_column='validUntil', blank=True, null=True, verbose_name='registered until')
    baseCountry = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='baseCountry', verbose_name='base country')
    comment = models.TextField('notes', blank=True, null=True)
    reminder = models.DateField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return(self.shortname or f'[id={self.id}]')

    def save(self, *args, **kwargs):
        if self.organisation is not None and self.organisation.acronym:
            self.shortname = self.organisation.acronym
        if self.deqarId:
            slug = slugify(f'{self.deqarId} {str(self)}')
            self.registerUrl = f'{self.T_BASE_URL}{slug}'
        else:
            self.registerUrl = None
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return(self.registerUrl)

    class Meta:
        db_table = 'registeredAgency'
        verbose_name_plural = 'registered agencies'
        ordering = [ 'shortname' ]


class AgencyUpdate(models.Model):
    TYPE_CHOICES = [
        ('institutional',   'Instituional reviews'),
        ('programme',       'Programme-level reviews'),
        ('joint programme', 'Joint programme reviews'),
    ]
    SOURCE_CHOICES = [
        ('DEQAR',   'Reports in DEQAR'),
        ('form',    'Annual survey'),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='uid')
    agency = models.ForeignKey(RegisteredAgency, on_delete=models.CASCADE, db_column='rid')
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country')
    year = models.IntegerField()
    type = EnumField(choices=TYPE_CHOICES)
    amount = models.IntegerField(blank=True, null=True)
    crossBorder = models.BooleanField("cross-border", default=False, db_column='crossBorder')
    source = EnumField(choices=SOURCE_CHOICES)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def __str__(self):
        return(f'{self.agency} {self.year} @ {self.country.iso3} ({self.type})')

    class Meta:
        db_table = 'agencyUpdate'
        unique_together = (('agency', 'country', 'year', 'type', 'source'),)
        ordering = [ 'agency', '-year', 'country' ]
        verbose_name = 'agency annual update'


class Applications(models.Model):
    TYPE_CHOICES = [
        ('Initial', 'Initial application for registration'),
        ('Renewal', 'Application for renewal of registration'),
    ]
    STAGE_CHOICES = [
        ('1. Eligibility check', '1. Eligibility check'),
        ('2. Waiting report', '2. Waiting report'),
        ('3. First consideration', '3. First consideration'),
        ('4. Waiting representation', '4. Waiting representation'),
        ('5. Second consideration', '5. Second consideration'),
        ('6. Waiting appeal', '6. Waiting appeal'),
        ('7. Appeal consideration', '7. Appeal consideration'),
        ('8. Completed', '8. Completed'),
        ('-- Withdrawn', '-- Withdrawn'),
    ]
    PANEL_CHOICES = [
        ('Full compliance',         'Full compliance'),
        ('Substantial compliance',  'Substantial compliance'),
        ('Partial compliance',      'Partial compliance'),
        ('Non-compliance',          'Non-compliance'),
    ]
    EQAR_CHOICES = [
        ('Compliance',              'Compliance'),
        ('Partial compliance',      'Partial compliance'),
        ('Non-compliance',          'Non-compliance'),
    ]
    RESULT_CHOICES = [
        ('Approved',    'Approved'),
        ('Rejected',    'Rejected'),
        ('Withdrawn',   'Withdrawn'),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='aid')
    agency = models.ForeignKey(RegisteredAgency, on_delete=models.RESTRICT, db_column='rid')
    selectName = models.CharField(editable=False, blank=True, db_column='selectName', max_length=255, null=True)
    submitDate = models.DateField("submitted on", db_column='submitDate', blank=False, null=False)
    type = EnumField(choices=TYPE_CHOICES, blank=False)
    stage = EnumField(choices=STAGE_CHOICES, blank=False)
    eligibilityDate = models.DateField("eligibility confirmed on", db_column='eligibilityDate', blank=True, null=True)
    reportExpected = models.DateField("report expected by", db_column='reportExpected', blank=True, null=True)
    reportDate = models.DateField("report date", db_column='reportDate', blank=True, null=True)
    reportSubmitted = models.DateField("report submitted on", db_column='reportSubmitted', blank=True, null=True)
    teleconfDate = models.DateField("teleconference on", db_column='teleconfDate', blank=True, null=True)
    rapporteur1 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur1', blank=True, null=True,
                                                    related_name='application_rapporteur1', verbose_name='rapporteur')
    rapporteur2 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur2', blank=True, null=True,
                                                    related_name='application_rapporteur2', verbose_name='rapporteur')
    rapporteur3 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur3', blank=True, null=True,
                                                    related_name='application_rapporteur3', verbose_name='third rapporteur')
    secretary =     models.ForeignKey(Contact,      on_delete=models.RESTRICT, db_column='secretary',   blank=True, null=True, related_name='application_secretary'  )
    coordinator =   models.ForeignKey(Organisation, on_delete=models.RESTRICT, db_column='coordinator', blank=True, null=True )
    roles =         models.ManyToManyField('contacts.Contact', through='ApplicationRole', related_name='application_role')
    interests =     models.ManyToManyField('contacts.Contact', through='ApplicationInterest', related_name='application_interest')
    panel_2_1 = EnumField("ESG 2.1 panel/rapporteurs/RC", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_2 = EnumField("ESG 2.2", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_3 = EnumField("ESG 2.3", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_4 = EnumField("ESG 2.4", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_5 = EnumField("ESG 2.5", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_6 = EnumField("ESG 2.6", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_7 = EnumField("ESG 2.7", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_1 = EnumField("ESG 3.1", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_2 = EnumField("ESG 3.2", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_3 = EnumField("ESG 3.3", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_4 = EnumField("ESG 3.4", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_5 = EnumField("ESG 3.5", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_6 = EnumField("ESG 3.6", choices=PANEL_CHOICES, blank=True, null=True)
    rapp_2_1 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_2 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_3 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_4 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_5 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_6 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_7 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_1 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_2 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_3 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_4 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_5 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_6 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_1 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_2 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_3 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_4 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_5 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_6 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_7 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_1 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_2 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_3 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_4 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_5 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_6 = EnumField(choices=EQAR_CHOICES, blank=True, null=True)
    invoiceNo = models.IntegerField(db_column='invoiceNo', unique=True, blank=True, null=True, verbose_name='invoice no.')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decisionDate = models.DateField(db_column='decisionDate', blank=True, null=True, verbose_name='decision of')
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def save(self, *args, **kwargs):
        self.selectName = str(self)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'applications'
        ordering = [ '-id' ]
        verbose_name = 'application'

    def __str__(self):
        return(f'A{self.id} {self.agency} ({self.submitDate.year} {self.type})')


class ApplicationClarification(models.Model):
    TYPE_CHOICES = [
        ('Panel',       'Panel'),
        ('Coordinator', 'Coordinator'),
        ('Agency',      'Agency'),
        ('Other',       'Other'),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='acid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    type = EnumField(choices=TYPE_CHOICES, blank=False)
    sentOn = models.DateField(db_column='sentOn', blank=True, null=True, verbose_name='request sent on')
    replyOn = models.DateField(db_column='replyOn', blank=True, null=True, verbose_name='reply received on')
    recipientOrg = models.ForeignKey(Organisation, on_delete=models.RESTRICT, db_column='recipientOrg', blank=True, null=True, verbose_name='recipient (organisation)')
    recipientContact = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='recipientContact', blank=True, null=True, verbose_name='recipient (individual)')
    esg_2_1 = models.BooleanField("ESG 2.1", default=False)
    esg_2_2 = models.BooleanField("ESG 2.2", default=False)
    esg_2_3 = models.BooleanField("ESG 2.3", default=False)
    esg_2_4 = models.BooleanField("ESG 2.4", default=False)
    esg_2_5 = models.BooleanField("ESG 2.5", default=False)
    esg_2_6 = models.BooleanField("ESG 2.6", default=False)
    esg_2_7 = models.BooleanField("ESG 2.7", default=False)
    esg_3_1 = models.BooleanField("ESG 3.1", default=False)
    esg_3_2 = models.BooleanField("ESG 3.2", default=False)
    esg_3_3 = models.BooleanField("ESG 3.3", default=False)
    esg_3_4 = models.BooleanField("ESG 3.4", default=False)
    esg_3_5 = models.BooleanField("ESG 3.5", default=False)
    esg_3_6 = models.BooleanField("ESG 3.6", default=False)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    class Meta:
        db_table = 'applicationClarification'
        verbose_name = 'clarification request'
        ordering = [ '-sentOn' ]

    def __str__(self):
        return(f'{self.application} - {self.type}')


class ApplicationInterest(models.Model):
    id = models.AutoField('ID', primary_key=True, db_column='aiid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid', verbose_name='person')
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    class Meta:
        db_table = 'applicationInterest'
        verbose_name = 'conflict of interest (application)'
        verbose_name_plural = 'conflicts of interest (application)'

    def __str__(self):
        return(f'{self.application} - {self.contact}')


class ApplicationRole(models.Model):
    ROLE_CHOICES = [
        ('Panel member',    'Panel member'      ),
        ('Panel chair',     'Panel chair'       ),
        ('Panel secretary', 'Panel secretary'   ),
        ('Coordinator',     'Coordinator'       ),
        ('Other',           'Other'             ),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='arid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid', verbose_name='person')
    role = EnumField(choices=ROLE_CHOICES, blank=False)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    class Meta:
        db_table = 'applicationRole'
        verbose_name = 'panel member'

    def __str__(self):
        return(f'{self.application} - {self.role}: {self.contact}')


class ChangeReport(models.Model):
    STAGE_CHOICES = [
        ('1. Analysis by Secretariat',  '1. Analysis by Secretariat'    ),
        ('2. Sent to rapporteurs',      '2. Sent to rapporteurs'        ),
        ('3. Waiting RC consideration', '3. Waiting RC consideration'   ),
        ('4. Completed',                '4. Completed'                  ),
    ]
    RESULT_CHOICES = [
        ('Take note',                               'Take note'                             ),
        ('Take note + further report',              'Take note + further report'            ),
        ('Extraordinary revision of registration',  'Extraordinary revision of registration'),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='crid')
    agency = models.ForeignKey(RegisteredAgency, models.DO_NOTHING, db_column='rid')
    selectName = models.CharField(editable=False, blank=True, db_column='selectName', max_length=255, null=True)
    submitDate = models.DateField(db_column='submitDate', blank=True, null=True, verbose_name='submitted on')
    stage = EnumField(choices=STAGE_CHOICES, blank=False)
    rapporteur1 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur1', blank=True, null=True,
                                    related_name='change_report_rapporteur1', verbose_name='rapporteur')
    rapporteur2 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur2', blank=True, null=True,
                                    related_name='change_report_rapporteur2', verbose_name='rapporteur')
    secretary = models.ForeignKey(Contact, models.DO_NOTHING, db_column='secretary', blank=True, null=True, related_name='change_report_secretary')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decisionDate = models.DateField(db_column='decisionDate', blank=True, null=True, verbose_name='decision of')
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    def save(self, *args, **kwargs):
        self.selectName = str(self)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'changeReport'
        verbose_name = 'Substantive Change Report'

    def __str__(self):
        return(f'C{self.id} {self.agency} ({self.submitDate.year})')


class Complaint(models.Model):
    STAGE_CHOICES = [
        ('1. Analysis by Secretariat',  '1. Analysis by Secretariat'    ),
        ('2. Sent to rapporteurs',      '2. Sent to rapporteurs'        ),
        ('3. Waiting RC consideration', '3. Waiting RC consideration'   ),
        ('4. Completed',                '4. Completed'                  ),
    ]
    RESULT_CHOICES = [
        ('Inadmissible',                            'Inadmissible'                          ),
        ('Rejected (not substantiated)',            'Rejected (not substantiated)'          ),
        ('Formal warning',                          'Formal warning'                        ),
        ('Extraordinary revision of registration',  'Extraordinary revision of registration'),
    ]

    id = models.AutoField('ID', primary_key=True, db_column='coid')
    agency = models.ForeignKey(RegisteredAgency, models.DO_NOTHING, db_column='rid')
    submitDate = models.DateField(db_column='submitDate', blank=True, null=True, verbose_name='submitted on')
    stage = EnumField(choices=STAGE_CHOICES)
    rapporteur1 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur1', blank=True, null=True,
                                    related_name='complaint_rapporteur1', verbose_name='rapporteur')
    rapporteur2 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur2', blank=True, null=True,
                                    related_name='complaint_rapporteur2', verbose_name='rapporteur')
    secretary = models.ForeignKey(Contact, models.DO_NOTHING, db_column='secretary', blank=True, null=True, related_name='complaint_secretary')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decisionDate = models.DateField(db_column='decisionDate', blank=True, null=True, verbose_name='decision of')
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    class Meta:
        db_table = 'complaint'

    def __str__(self):
        return(f'CO{self.id} {self.agency}: {self.result or "(in progress)"}')

