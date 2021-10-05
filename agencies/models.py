from django.db import models
from django.template.defaultfilters import slugify

from contacts.models import Organisation, Contact, OctopusAccount, Country, ContactOrganisation
from uni_db.fields import EnumField

"""
Agencies: everything related to registered agencies, applications, etc.
"""

class RegisteredAgency(models.Model):
    T_BASE_URL = 'https://data.deqar.eu/agency/'

    id = models.AutoField(primary_key=True, db_column='rid')
    organisation = models.OneToOneField(Organisation, on_delete=models.RESTRICT, db_column='oid', blank=True, null=True)
    octopus_account = models.OneToOneField(OctopusAccount, on_delete=models.RESTRICT, db_column='oaid', blank=True, null=True)
    shortname = models.CharField(max_length=255, blank=True, null=True)
    main_contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='mainContact', blank=True, null=True, related_name='agency_main')  # Field name made lowercase.
    web_contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='webContact', blank=True, null=True, related_name='agency_web')  # Field name made lowercase.
    registered = models.BooleanField(default=False)
    deqar_id = models.IntegerField(db_column='deqarId', unique=True, blank=True, null=True)  # Field name made lowercase.
    registered_since = models.DateField(db_column='registeredSince', blank=True, null=True)  # Field name made lowercase.
    valid_until = models.DateField(db_column='validUntil', blank=True, null=True)  # Field name made lowercase.
    base_country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='baseCountry')  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)
    reminder = models.DateField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return(self.shortname)

    @property
    def register_url(self):
        return('{}{}'.format(self.T_BASE_URL, slugify('{0.deqar_id} {0.shortname}'.format(self))))

    def get_absolute_url(self):
        return(self.register_url)

    class Meta:
        db_table = 'registeredAgency'
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

    id = models.AutoField(primary_key=True, db_column='uid')
    agency = models.ForeignKey(RegisteredAgency, on_delete=models.CASCADE, db_column='rid')
    country = models.ForeignKey(Country, on_delete=models.RESTRICT, db_column='country')
    year = models.IntegerField()
    type = EnumField(choices=TYPE_CHOICES)
    amount = models.IntegerField(blank=True, null=True)
    cross_border = models.BooleanField(default=False, db_column='crossBorder')  # Field name made lowercase.
    source = EnumField(choices=SOURCE_CHOICES)
    mtime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return('{} {} @ {} ({})'.format(self.agency, self.year, self.country.iso3, self.type))

    class Meta:
        db_table = 'agencyUpdate'
        unique_together = (('agency', 'country', 'year', 'type', 'source'),)
        ordering = [ 'agency', '-year', 'country' ]


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

    id = models.AutoField(primary_key=True, db_column='aid')
    agency = models.ForeignKey(RegisteredAgency, on_delete=models.RESTRICT, db_column='rid')
    submit_date = models.DateField(db_column='submitDate', blank=False, null=False)  # Field name made lowercase.
    type = EnumField(choices=TYPE_CHOICES, blank=False)
    stage = EnumField(choices=STAGE_CHOICES, blank=False)
    eligibility_date = models.DateField(db_column='eligibilityDate', blank=True, null=True)  # Field name made lowercase.
    report_expected = models.DateField(db_column='reportExpected', blank=True, null=True)  # Field name made lowercase.
    report_date = models.DateField(db_column='reportDate', blank=True, null=True)  # Field name made lowercase.
    report_submitted = models.DateField(db_column='reportSubmitted', blank=True, null=True)  # Field name made lowercase.
    teleconf_date = models.DateField(db_column='teleconfDate', blank=True, null=True)  # Field name made lowercase.
    rapporteur1 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur1', blank=True, null=True, related_name='application_rapporteur1')
    rapporteur2 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur2', blank=True, null=True, related_name='application_rapporteur2')
    rapporteur3 =   models.ForeignKey(Contact,      on_delete=models.SET_NULL, db_column='rapporteur3', blank=True, null=True, related_name='application_rapporteur3')
    secretary =     models.ForeignKey(Contact,      on_delete=models.RESTRICT, db_column='secretary',   blank=True, null=True, related_name='application_secretary'  )
    coordinator =   models.ForeignKey(Organisation, on_delete=models.RESTRICT, db_column='coordinator', blank=True, null=True )
    panel_2_1 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_2 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_3 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_4 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_5 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_6 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_2_7 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_1 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_2 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_3 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_4 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_5 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
    panel_3_6 = EnumField(choices=PANEL_CHOICES, blank=True, null=True)
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
    invoice_no = models.IntegerField(db_column='invoiceNo', unique=True, blank=True, null=True)  # Field name made lowercase.
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decision_date = models.DateField(db_column='decisionDate', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        ordering = [ '-id' ]

    def __str__(self):
        return('A{} {} ({} {})'.format(self.id, self.agency, self.submit_date.year, self.type))


class ApplicationClarification(models.Model):
    TYPE_CHOICES = [
        ('Panel',       'Panel'),
        ('Coordinator', 'Coordinator'),
        ('Agency',      'Agency'),
        ('Other',       'Other'),
    ]

    id = models.AutoField(primary_key=True, db_column='acid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    type = EnumField(choices=TYPE_CHOICES, blank=False)
    sent_on = models.DateField(db_column='sentOn', blank=True, null=True)  # Field name made lowercase.
    reply_on = models.DateField(db_column='replyOn', blank=True, null=True)  # Field name made lowercase.
    recipient_org = models.ForeignKey(Organisation, on_delete=models.RESTRICT, db_column='recipientOrg', blank=True, null=True)  # Field name made lowercase.
    recipient_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, db_column='recipientContact', blank=True, null=True)  # Field name made lowercase.
    esg_2_1 = models.BooleanField(default=False)
    esg_2_2 = models.BooleanField(default=False)
    esg_2_3 = models.BooleanField(default=False)
    esg_2_4 = models.BooleanField(default=False)
    esg_2_5 = models.BooleanField(default=False)
    esg_2_6 = models.BooleanField(default=False)
    esg_2_7 = models.BooleanField(default=False)
    esg_3_1 = models.BooleanField(default=False)
    esg_3_2 = models.BooleanField(default=False)
    esg_3_3 = models.BooleanField(default=False)
    esg_3_4 = models.BooleanField(default=False)
    esg_3_5 = models.BooleanField(default=False)
    esg_3_6 = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applicationClarification'

    def __str__(self):
        return('{} - {}'.format(self.application, self.type))


class ApplicationInterest(models.Model):
    id = models.AutoField(primary_key=True, db_column='aiid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid')
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applicationInterest'

    def __str__(self):
        return('{} - {}'.format(self.application, self.contact))


class ApplicationRole(models.Model):
    ROLE_CHOICES = [
        ('Panel member',    'Panel member'      ),
        ('Panel chair',     'Panel chair'       ),
        ('Panel secretary', 'Panel secretary'   ),
        ('Coordinator',     'Coordinator'       ),
        ('Other',           'Other'             ),
    ]

    id = models.AutoField(primary_key=True, db_column='arid')
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, db_column='aid')
    contact = models.ForeignKey(Contact, on_delete=models.RESTRICT, db_column='cid')
    role = EnumField(choices=ROLE_CHOICES, blank=False)
    notes = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applicationRole'

    def __str__(self):
        return('{} - {}: {}'.format(self.application, self.role, self.contact))


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

    id = models.AutoField(primary_key=True, db_column='crid')
    agency = models.ForeignKey(RegisteredAgency, models.DO_NOTHING, db_column='rid')
    submit_date = models.DateField(db_column='submitDate', blank=True, null=True)  # Field name made lowercase.
    stage = EnumField(choices=STAGE_CHOICES, blank=False)
    rapporteur1 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur1', blank=True, null=True, related_name='change_report_rapporteur1')
    rapporteur2 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur2', blank=True, null=True, related_name='change_report_rapporteur2')
    secretary = models.ForeignKey(Contact, models.DO_NOTHING, db_column='secretary', blank=True, null=True, related_name='change_report_secretary')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decision_date = models.DateField(db_column='decisionDate', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'changeReport'

    def __str__(self):
        return('C{} {} ({})'.format(self.id, self.agency, self.submit_date.year))


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

    id = models.AutoField(primary_key=True, db_column='coid')
    agency = models.ForeignKey(RegisteredAgency, models.DO_NOTHING, db_column='rid')
    submit_date = models.DateField(db_column='submitDate', blank=True, null=True)  # Field name made lowercase.
    stage = EnumField(choices=STAGE_CHOICES)
    rapporteur1 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur1', blank=True, null=True, related_name='complaint_rapporteur1')
    rapporteur2 = models.ForeignKey(Contact, models.DO_NOTHING, db_column='rapporteur2', blank=True, null=True, related_name='complaint_rapporteur2')
    secretary = models.ForeignKey(Contact, models.DO_NOTHING, db_column='secretary', blank=True, null=True, related_name='complaint_secretary')
    result = EnumField(choices=RESULT_CHOICES, blank=True, null=True)
    decision_date = models.DateField(db_column='decisionDate', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'complaint'

    def __str__(self):
        return('CO{} {}: {}'.format(self.id, self.agency, self.result or '(in progress)'))

