# Generated by Django 3.1.2 on 2021-10-17 21:06

from django.db import migrations, models
import django.db.models.deletion
import uni_db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegisteredAgency',
            fields=[
                ('id', models.AutoField(db_column='rid', primary_key=True, serialize=False, verbose_name='Agency ID')),
                ('shortname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Acronym')),
                ('registered', models.BooleanField(default=False)),
                ('deqarId', models.IntegerField(blank=True, db_column='deqarId', null=True, unique=True, verbose_name='DEQAR ID')),
                ('registerUrl', models.CharField(blank=True, db_column='registerUrl', max_length=255, null=True)),
                ('registeredSince', models.DateField(blank=True, db_column='registeredSince', null=True, verbose_name='registered since')),
                ('validUntil', models.DateField(blank=True, db_column='validUntil', null=True, verbose_name='registered until')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('reminder', models.DateField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('baseCountry', models.ForeignKey(db_column='baseCountry', on_delete=django.db.models.deletion.RESTRICT, to='contacts.country', verbose_name='base country')),
                ('mainContact', models.ForeignKey(blank=True, db_column='mainContact', null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='agency_main', to='contacts.contact', verbose_name='main contact')),
                ('octopusAccount', models.OneToOneField(blank=True, db_column='oaid', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.octopusaccount', verbose_name='financial account')),
                ('organisation', models.OneToOneField(blank=True, db_column='oid', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
                ('webContact', models.ForeignKey(blank=True, db_column='webContact', null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='agency_web', to='contacts.contact', verbose_name='website contact')),
            ],
            options={
                'verbose_name_plural': 'registered agencies',
                'db_table': 'registeredAgency',
                'ordering': ['shortname'],
            },
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(db_column='coid', primary_key=True, serialize=False, verbose_name='ID')),
                ('submitDate', models.DateField(blank=True, db_column='submitDate', null=True, verbose_name='submitted on')),
                ('stage', uni_db.fields.EnumField(choices=[('1. Analysis by Secretariat', '1. Analysis by Secretariat'), ('2. Sent to rapporteurs', '2. Sent to rapporteurs'), ('3. Waiting RC consideration', '3. Waiting RC consideration'), ('4. Completed', '4. Completed')])),
                ('result', uni_db.fields.EnumField(blank=True, choices=[('Inadmissible', 'Inadmissible'), ('Rejected (not substantiated)', 'Rejected (not substantiated)'), ('Formal warning', 'Formal warning'), ('Extraordinary revision of registration', 'Extraordinary revision of registration')], null=True)),
                ('decisionDate', models.DateField(blank=True, db_column='decisionDate', null=True, verbose_name='decision of')),
                ('comment', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('agency', models.ForeignKey(db_column='rid', on_delete=django.db.models.deletion.DO_NOTHING, to='agencies.registeredagency')),
                ('rapporteur1', models.ForeignKey(blank=True, db_column='rapporteur1', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='complaint_rapporteur1', to='contacts.contact', verbose_name='rapporteur')),
                ('rapporteur2', models.ForeignKey(blank=True, db_column='rapporteur2', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='complaint_rapporteur2', to='contacts.contact', verbose_name='rapporteur')),
                ('secretary', models.ForeignKey(blank=True, db_column='secretary', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='complaint_secretary', to='contacts.contact')),
            ],
            options={
                'db_table': 'complaint',
            },
        ),
        migrations.CreateModel(
            name='ChangeReport',
            fields=[
                ('id', models.AutoField(db_column='crid', primary_key=True, serialize=False, verbose_name='ID')),
                ('submitDate', models.DateField(blank=True, db_column='submitDate', null=True, verbose_name='submitted on')),
                ('stage', uni_db.fields.EnumField(choices=[('1. Analysis by Secretariat', '1. Analysis by Secretariat'), ('2. Sent to rapporteurs', '2. Sent to rapporteurs'), ('3. Waiting RC consideration', '3. Waiting RC consideration'), ('4. Completed', '4. Completed')])),
                ('result', uni_db.fields.EnumField(blank=True, choices=[('Take note', 'Take note'), ('Take note + further report', 'Take note + further report'), ('Extraordinary revision of registration', 'Extraordinary revision of registration')], null=True)),
                ('decisionDate', models.DateField(blank=True, db_column='decisionDate', null=True, verbose_name='decision of')),
                ('comment', models.TextField(blank=True, null=True)),
                ('selectName', models.CharField(blank=True, db_column='selectName', max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('agency', models.ForeignKey(db_column='rid', on_delete=django.db.models.deletion.DO_NOTHING, to='agencies.registeredagency')),
                ('rapporteur1', models.ForeignKey(blank=True, db_column='rapporteur1', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='change_report_rapporteur1', to='contacts.contact')),
                ('rapporteur2', models.ForeignKey(blank=True, db_column='rapporteur2', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='change_report_rapporteur2', to='contacts.contact', verbose_name='rapporteur')),
                ('secretary', models.ForeignKey(blank=True, db_column='secretary', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='change_report_secretary', to='contacts.contact')),
            ],
            options={
                'verbose_name': 'Substantive Change Report',
                'db_table': 'changeReport',
            },
        ),
        migrations.CreateModel(
            name='Applications',
            fields=[
                ('id', models.AutoField(db_column='aid', primary_key=True, serialize=False, verbose_name='ID')),
                ('submitDate', models.DateField(db_column='submitDate', verbose_name='submitted on')),
                ('type', uni_db.fields.EnumField(choices=[('Initial', 'Initial application for registration'), ('Renewal', 'Application for renewal of registration')])),
                ('stage', uni_db.fields.EnumField(choices=[('1. Eligibility check', '1. Eligibility check'), ('2. Waiting report', '2. Waiting report'), ('3. First consideration', '3. First consideration'), ('4. Waiting representation', '4. Waiting representation'), ('5. Second consideration', '5. Second consideration'), ('6. Waiting appeal', '6. Waiting appeal'), ('7. Appeal consideration', '7. Appeal consideration'), ('8. Completed', '8. Completed'), ('-- Withdrawn', '-- Withdrawn')])),
                ('eligibilityDate', models.DateField(blank=True, db_column='eligibilityDate', null=True, verbose_name='eligibility confirmed on')),
                ('reportExpected', models.DateField(blank=True, db_column='reportExpected', null=True, verbose_name='report expected by')),
                ('reportDate', models.DateField(blank=True, db_column='reportDate', null=True, verbose_name='report date')),
                ('reportSubmitted', models.DateField(blank=True, db_column='reportSubmitted', null=True, verbose_name='report submitted on')),
                ('teleconfDate', models.DateField(blank=True, db_column='teleconfDate', null=True, verbose_name='teleconference on')),
                ('panel_2_1', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.1 panel/rapporteurs/RC')),
                ('panel_2_2', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.2')),
                ('panel_2_3', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.3')),
                ('panel_2_4', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.4')),
                ('panel_2_5', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.5')),
                ('panel_2_6', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.6')),
                ('panel_2_7', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.7')),
                ('panel_3_1', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.1')),
                ('panel_3_2', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.2')),
                ('panel_3_3', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.3')),
                ('panel_3_4', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.4')),
                ('panel_3_5', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.5')),
                ('panel_3_6', uni_db.fields.EnumField(blank=True, choices=[('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.6')),
                ('rapp_2_1', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_2', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_3', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_4', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_5', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_6', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_2_7', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_1', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_2', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_3', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_4', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_5', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rapp_3_6', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_1', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_2', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_3', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_4', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_5', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_6', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_2_7', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_1', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_2', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_3', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_4', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_5', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('rc_3_6', uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True)),
                ('invoiceNo', models.IntegerField(blank=True, db_column='invoiceNo', null=True, unique=True, verbose_name='invoice no.')),
                ('result', uni_db.fields.EnumField(blank=True, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Withdrawn', 'Withdrawn')], null=True)),
                ('decisionDate', models.DateField(blank=True, db_column='decisionDate', null=True, verbose_name='decision of')),
                ('comment', models.TextField(blank=True, null=True)),
                ('selectName', models.CharField(blank=True, db_column='selectName', max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('agency', models.ForeignKey(db_column='rid', on_delete=django.db.models.deletion.RESTRICT, to='agencies.registeredagency')),
                ('coordinator', models.ForeignKey(blank=True, db_column='coordinator', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
                ('rapporteur1', models.ForeignKey(blank=True, db_column='rapporteur1', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='application_rapporteur1', to='contacts.contact', verbose_name='rapporteur')),
                ('rapporteur2', models.ForeignKey(blank=True, db_column='rapporteur2', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='application_rapporteur2', to='contacts.contact', verbose_name='rapporteur')),
                ('rapporteur3', models.ForeignKey(blank=True, db_column='rapporteur3', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='application_rapporteur3', to='contacts.contact', verbose_name='third rapporteur')),
                ('secretary', models.ForeignKey(blank=True, db_column='secretary', null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='application_secretary', to='contacts.contact')),
            ],
            options={
                'verbose_name': 'application',
                'db_table': 'applications',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ApplicationRole',
            fields=[
                ('id', models.AutoField(db_column='arid', primary_key=True, serialize=False, verbose_name='ID')),
                ('role', uni_db.fields.EnumField(choices=[('Panel member', 'Panel member'), ('Panel chair', 'Panel chair'), ('Panel secretary', 'Panel secretary'), ('Coordinator', 'Coordinator'), ('Other', 'Other')])),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('application', models.ForeignKey(db_column='aid', on_delete=django.db.models.deletion.CASCADE, to='agencies.applications')),
                ('contact', models.ForeignKey(db_column='cid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.contact', verbose_name='person')),
            ],
            options={
                'verbose_name': 'panel member',
                'db_table': 'applicationRole',
            },
        ),
        migrations.CreateModel(
            name='ApplicationInterest',
            fields=[
                ('id', models.AutoField(db_column='aiid', primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('application', models.ForeignKey(db_column='aid', on_delete=django.db.models.deletion.CASCADE, to='agencies.applications')),
                ('contact', models.ForeignKey(db_column='cid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.contact', verbose_name='person')),
            ],
            options={
                'verbose_name': 'conflict of interest (application)',
                'verbose_name_plural': 'conflicts of interest (application)',
                'db_table': 'applicationInterest',
            },
        ),
        migrations.CreateModel(
            name='ApplicationClarification',
            fields=[
                ('id', models.AutoField(db_column='acid', primary_key=True, serialize=False, verbose_name='ID')),
                ('type', uni_db.fields.EnumField(choices=[('Panel', 'Panel'), ('Coordinator', 'Coordinator'), ('Agency', 'Agency'), ('Other', 'Other')])),
                ('sentOn', models.DateField(blank=True, db_column='sentOn', null=True, verbose_name='request sent on')),
                ('replyOn', models.DateField(blank=True, db_column='replyOn', null=True, verbose_name='reply received on')),
                ('esg_2_1', models.BooleanField(default=False, verbose_name='ESG 2.1')),
                ('esg_2_2', models.BooleanField(default=False, verbose_name='ESG 2.2')),
                ('esg_2_3', models.BooleanField(default=False, verbose_name='ESG 2.3')),
                ('esg_2_4', models.BooleanField(default=False, verbose_name='ESG 2.4')),
                ('esg_2_5', models.BooleanField(default=False, verbose_name='ESG 2.5')),
                ('esg_2_6', models.BooleanField(default=False, verbose_name='ESG 2.6')),
                ('esg_2_7', models.BooleanField(default=False, verbose_name='ESG 2.7')),
                ('esg_3_1', models.BooleanField(default=False, verbose_name='ESG 3.1')),
                ('esg_3_2', models.BooleanField(default=False, verbose_name='ESG 3.2')),
                ('esg_3_3', models.BooleanField(default=False, verbose_name='ESG 3.3')),
                ('esg_3_4', models.BooleanField(default=False, verbose_name='ESG 3.4')),
                ('esg_3_5', models.BooleanField(default=False, verbose_name='ESG 3.5')),
                ('esg_3_6', models.BooleanField(default=False, verbose_name='ESG 3.6')),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('application', models.ForeignKey(db_column='aid', on_delete=django.db.models.deletion.CASCADE, to='agencies.applications')),
                ('recipientContact', models.ForeignKey(blank=True, db_column='recipientContact', null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.contact', verbose_name='recipient (individual)')),
                ('recipientOrg', models.ForeignKey(blank=True, db_column='recipientOrg', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation', verbose_name='recipient (organisation)')),
            ],
            options={
                'verbose_name': 'clarification request',
                'db_table': 'applicationClarification',
                'ordering': ['-sentOn'],
            },
        ),
        migrations.CreateModel(
            name='AgencyUpdate',
            fields=[
                ('id', models.AutoField(db_column='uid', primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('type', uni_db.fields.EnumField(choices=[('institutional', 'Instituional reviews'), ('programme', 'Programme-level reviews'), ('joint programme', 'Joint programme reviews')])),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('crossBorder', models.BooleanField(db_column='crossBorder', default=False, verbose_name='cross-border')),
                ('source', uni_db.fields.EnumField(choices=[('DEQAR', 'Reports in DEQAR'), ('form', 'Annual survey')])),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('agency', models.ForeignKey(db_column='rid', on_delete=django.db.models.deletion.CASCADE, to='agencies.registeredagency')),
                ('country', models.ForeignKey(db_column='country', on_delete=django.db.models.deletion.RESTRICT, to='contacts.country')),
            ],
            options={
                'verbose_name': 'agency annual update',
                'db_table': 'agencyUpdate',
                'ordering': ['agency', '-year', 'country'],
                'unique_together': {('agency', 'country', 'year', 'type', 'source')},
            },
        ),
    ]
