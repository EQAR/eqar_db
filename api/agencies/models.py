from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.template.defaultfilters import slugify

from contacts.models import Organisation, Contact, OctopusAccount, Country, ContactOrganisation
from uni_db.fields import EnumField
from uni_db.validators import validate_date_in_past

"""
Agencies: everything related to registered agencies, applications, etc.
"""

class RegisteredAgency(models.Model):
    T_BASE_URL = 'https://data.deqar.eu/agency/'

    id = models.AutoField('Agency ID', primary_key=True, db_column='rid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid')
    octopusAccount = models.OneToOneField(OctopusAccount, on_delete=models.RESTRICT, db_column='oaid', blank=True, null=True, verbose_name='financial account')
    shortname = models.CharField('Acronym', max_length=255, blank=True, editable=False)
    mainContact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='mainContact', blank=True, null=True,
                                        related_name='agency_main', verbose_name='main contact')
    registered = models.BooleanField(default=False)
    deqarId = models.IntegerField(db_column='deqarId', unique=True, blank=True, null=True, verbose_name='DEQAR ID')
    registerUrl = models.CharField(editable=False, blank=True, db_column='registerUrl', max_length=255, null=True, verbose_name='register entry URL')
    registeredSince = models.DateField(db_column='registeredSince', blank=True, null=True, verbose_name='registered since')
    validUntil = models.DateField(db_column='validUntil', blank=True, null=True, verbose_name='registered until')
    baseCountry = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='baseCountry', verbose_name='base country')
    comment = models.TextField('notes', blank=True, null=True)
    reminder = models.DateField(blank=True, null=True)
    mtime = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return(self.shortname or f'[id={self.id}]')

    def save(self, *args, **kwargs):
        if self.deqarId:
            slug = slugify(f'{self.deqarId} {str(self)}')
            self.registerUrl = f'{self.T_BASE_URL}{slug}'
        else:
            self.registerUrl = None
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return(self.registerUrl)

    def get_readonly_fields(self):
        if self.deqarId:
            return(['deqarId', 'registeredSince', 'validUntil', 'registered', 'baseCountry'])
        else:
            return([])

    class Meta:
        db_table = 'registeredAgency'
        verbose_name_plural = 'registered agencies'
        ordering = [ 'shortname' ]


class EsgVersion(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return(self.name)

    class Meta:
        verbose_name = 'ESG version'
        ordering = [ 'name' ]


class EsgStandard(models.Model):
    id = models.AutoField('ID', primary_key=True)
    version = models.ForeignKey(EsgVersion, on_delete=models.RESTRICT)
    part = models.CharField(max_length=3)
    number = models.CharField(max_length=3)
    title = models.CharField(max_length=255)

    def __str__(self):
        label = f'{self.part}.{self.number} {self.title}'
        if not self.version.active:
            label = label + f' ({self.version})'
        return(label)

    @property
    def attribute_name(self):
        return f'{self.part}_{self.number}'

    @property
    def short_name(self):
        return f'ESG {self.part}.{self.number}'

    class Meta:
        verbose_name = 'ESG standard'
        ordering = [ '-version__active', 'version__name', 'part', 'number' ]
        unique_together = ( ('version', 'part', 'number'), )


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
    REVIEW_CHOICES = [
        ('Full',        'Full review'),
        ('Focused',     'Focused review'),
        ('Targeted',    'Targeted review'),
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
        ('Compliance',              'Compliance'),
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
    submitDate = models.DateField("submitted on", db_column='submitDate', blank=False, null=False, validators=[validate_date_in_past])
    type = EnumField(choices=TYPE_CHOICES, blank=False)
    review = EnumField("type of review", choices=REVIEW_CHOICES, blank=False, default='Full')
    previous = models.ForeignKey('self',    on_delete=models.RESTRICT, blank=True, null=True,
                                            related_name='following', verbose_name='previous application')
    stage = EnumField(choices=STAGE_CHOICES, blank=False)
    eligibilityDate = models.DateField("eligibility confirmed on", db_column='eligibilityDate', blank=True, null=True)
    reportExpected = models.DateField("report expected by", db_column='reportExpected', blank=True, null=True)
    sitevisitDate = models.DateField("site-visit date", db_column='sitevisitDate', blank=True, null=True)
    reportDate = models.DateField("report date", db_column='reportDate', blank=True, null=True)
    reportSubmitted = models.DateField("report submitted on", db_column='reportSubmitted', blank=True, null=True)
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
    inherit_2_1 = models.BooleanField("inherit ESG 2.1", default=False)
    inherit_2_2 = models.BooleanField("inherit ESG 2.2", default=False)
    inherit_2_3 = models.BooleanField("inherit ESG 2.3", default=False)
    inherit_2_4 = models.BooleanField("inherit ESG 2.4", default=False)
    inherit_2_5 = models.BooleanField("inherit ESG 2.5", default=False)
    inherit_2_6 = models.BooleanField("inherit ESG 2.6", default=False)
    inherit_2_7 = models.BooleanField("inherit ESG 2.7", default=False)
    inherit_3_1 = models.BooleanField("inherit ESG 3.1", default=False)
    inherit_3_2 = models.BooleanField("inherit ESG 3.2", default=False)
    inherit_3_3 = models.BooleanField("inherit ESG 3.3", default=False)
    inherit_3_4 = models.BooleanField("inherit ESG 3.4", default=False)
    inherit_3_5 = models.BooleanField("inherit ESG 3.5", default=False)
    inherit_3_6 = models.BooleanField("inherit ESG 3.6", default=False)
    panel_2_1 = EnumField("ESG 2.1 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_2 = EnumField("ESG 2.2 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_3 = EnumField("ESG 2.3 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_4 = EnumField("ESG 2.4 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_5 = EnumField("ESG 2.5 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_6 = EnumField("ESG 2.6 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_7 = EnumField("ESG 2.7 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_1 = EnumField("ESG 3.1 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_2 = EnumField("ESG 3.2 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_3 = EnumField("ESG 3.3 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_4 = EnumField("ESG 3.4 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_5 = EnumField("ESG 3.5 panel", choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_6 = EnumField("ESG 3.6 panel", choices=PANEL_CHOICES, blank=True, null=True)
    rapp_2_1 = EnumField("ESG 2.1 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_2 = EnumField("ESG 2.2 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_3 = EnumField("ESG 2.3 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_4 = EnumField("ESG 2.4 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_5 = EnumField("ESG 2.5 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_6 = EnumField("ESG 2.6 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_2_7 = EnumField("ESG 2.7 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_1 = EnumField("ESG 3.1 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_2 = EnumField("ESG 3.2 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_3 = EnumField("ESG 3.3 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_4 = EnumField("ESG 3.4 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_5 = EnumField("ESG 3.5 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rapp_3_6 = EnumField("ESG 3.6 rapporteurs", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_1 = EnumField("ESG 2.1 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_2 = EnumField("ESG 2.2 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_3 = EnumField("ESG 2.3 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_4 = EnumField("ESG 2.4 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_5 = EnumField("ESG 2.5 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_6 = EnumField("ESG 2.6 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_2_7 = EnumField("ESG 2.7 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_1 = EnumField("ESG 3.1 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_2 = EnumField("ESG 3.2 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_3 = EnumField("ESG 3.3 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_4 = EnumField("ESG 3.4 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_5 = EnumField("ESG 3.5 RC", choices=EQAR_CHOICES, blank=True, null=True)
    rc_3_6 = EnumField("ESG 3.6 RC", choices=EQAR_CHOICES, blank=True, null=True)
    invoiceNo = models.IntegerField(db_column='invoiceNo', unique=True, blank=True, null=True, verbose_name='invoice no.')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decisionDate = models.DateField(db_column='decisionDate', blank=True, null=True, verbose_name='decision of')
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def save(self, *args, **kwargs):
        self.selectName = str(self)
        if self.id is None:
            previous_list = self.agency.applications_set.order_by('id')
        else:
            previous_list = self.agency.applications_set.filter(id__lt=self.id).order_by('id')
        if previous_list.count() > 0:
            self.previous = previous_list.last()
        else:
            self.previous = None
        for esg in EsgVersion.objects.get(active=True).esgstandard_set.all():
            if self.previous and self.review in [ 'Focused', 'Targeted' ] and getattr(self, f'inherit_{esg.attribute_name}'):
                setattr(self, f'panel_{esg.attribute_name}', getattr(self.previous, f'panel_{esg.attribute_name}'))
                setattr(self, f'rapp_{esg.attribute_name}', getattr(self.previous, f'rapp_{esg.attribute_name}'))
                setattr(self, f'rc_{esg.attribute_name}', getattr(self.previous, f'rc_{esg.attribute_name}'))
        super().save(*args, **kwargs)
        for esg in EsgVersion.objects.get(active=True).esgstandard_set.all():
            if getattr(self, f'panel_{esg.attribute_name}') or getattr(self, f'rapp_{esg.attribute_name}') or getattr(self, f'rc_{esg.attribute_name}'):
                ApplicationStandard.objects.update_or_create(
                    application=self,
                    standard=esg,
                    defaults=dict(
                        panel=getattr(self, f'panel_{esg.attribute_name}'),
                        rapporteurs=getattr(self, f'rapp_{esg.attribute_name}'),
                        rc=getattr(self, f'rc_{esg.attribute_name}')
                    )
                )

    def get_readonly_fields(self):
        readonly_fields = [ 'previous' ]
        for esg in EsgVersion.objects.get(active=True).esgstandard_set.all():
            if getattr(self, f'inherit_{esg.attribute_name}'):
                readonly_fields.append(f'panel_{esg.attribute_name}')
                readonly_fields.append(f'rapp_{esg.attribute_name}')
                readonly_fields.append(f'rc_{esg.attribute_name}')
        return readonly_fields

    def clean(self, *args, **kwargs):
        def require(field, msg):
            if getattr(self, field) is None or getattr(self, field) == '':
                errors[field] = msg

        super().clean(*args, **kwargs)
        errors = {}
        if self.type == 'Initial' and self.review == 'Targeted':
            errors["review"] = "Targeted reviews allowed only for Renewal."
        if self.stage >= '2': # waiting report
            require("eligibilityDate", "Date must be specified after eligibility stage.")
            require("reportExpected", "Date must be specified after eligibility stage.")
            require("coordinator", "Coordinator must be specified.")
            require("secretary", "EQAR team member must be specified.")
        if self.stage >= '3': # first consideration
            require("sitevisitDate", "Date must be specified.")
            require("reportDate", "Date must be specified.")
            require("reportSubmitted", "Date must be specified.")
        if self.stage >= '4': # waiting representation
            for esg in EsgVersion.objects.get(active=True).esgstandard_set.all():
                if not getattr(self, f'inherit_{esg.attribute_name}'):
                    require(f'panel_{esg.attribute_name}', "Must be specified.")
                    require(f'rapp_{esg.attribute_name}', "Must be specified.")
                    require(f'rc_{esg.attribute_name}', "Must be specified.")
        if self.stage >= '8': # completed
            require("result", "Decision needs to be specified for completed decisions.")
        if self.result:
            require("decisionDate", "Date must be specified.")
        if self.eligibilityDate and self.eligibilityDate < self.submitDate:
            errors["eligibilityDate"] = "Cannot be before submission date."
        for esg in EsgVersion.objects.get(active=True).esgstandard_set.all():
            if getattr(self, f'inherit_{esg.attribute_name}') and self.review not in [ 'Focused', 'Targeted' ]:
                errors[NON_FIELD_ERRORS] = "Inheriting compliance is only possible for focused or targeted reviews."
        if errors:
            raise ValidationError(errors)

    class Meta:
        db_table = 'applications'
        ordering = [ '-id' ]
        verbose_name = 'application'

    def __str__(self):
        return(f'A{self.id} {self.agency} ({self.submitDate.year} {self.type}, {self.review})')


class ApplicationStandard(models.Model):
    id = models.AutoField('ID', primary_key=True)
    application = models.ForeignKey(Applications, on_delete=models.RESTRICT, editable=False)
    standard = models.ForeignKey(EsgStandard, on_delete=models.RESTRICT, editable=False)
    panel = EnumField(choices=Applications.PANEL_CHOICES, editable=False, blank=True, null=True)
    rapporteurs = EnumField(choices=Applications.EQAR_CHOICES, editable=False, blank=True, null=True)
    rc = EnumField(choices=Applications.EQAR_CHOICES, editable=False, blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    decision = models.TextField(blank=True, null=True)
    internal_notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField("last modified", auto_now=True)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if (self.keywords is None or self.keywords == '') and self.decision is not None:
            raise ValidationError({ "keywords": "Keywords must be filled if decision text is filled." })

    class Meta:
        unique_together = ( ('application', 'standard'), )
        ordering = [ 'application', 'standard' ]

    def __str__(self):
        return(f'{self.standard.short_name} @ {self.application}')


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

