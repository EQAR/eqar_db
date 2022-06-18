# Generated by Django 3.1.2 on 2022-05-11 07:44

from django.db import migrations, models
import django.db.models.deletion

import re

def create_missing_organisations(apps, schema_editor):
    Organisation = apps.get_model('contacts', 'organisation')
    RegisteredAgency = apps.get_model('agencies', 'registeredagency')
    for agency in RegisteredAgency.objects.filter(organisation__isnull=True):
        acronym = re.sub('\s*\[historical\]\s*', '', agency.shortname)
        if acronym != agency.shortname:
            agency.shortname = acronym
        agency.organisation = Organisation.objects.create(acronym=acronym[:15], country=agency.baseCountry, role_id=1)
        agency.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_contactorganisation_onregister'),
        ('agencies', '0004_remove_registeredagency_webcontact'),
    ]

    operations = [
        migrations.RunPython(create_missing_organisations),
        migrations.AlterField(
            model_name='registeredagency',
            name='organisation',
            field=models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation'),
        ),
        migrations.AlterField(
            model_name='registeredagency',
            name='registerUrl',
            field=models.CharField(blank=True, db_column='registerUrl', editable=False, max_length=255, null=True, verbose_name='register entry URL'),
        ),
        migrations.AlterField(
            model_name='registeredagency',
            name='shortname',
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name='Acronym'),
        ),
    ]
