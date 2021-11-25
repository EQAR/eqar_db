# Generated by Django 3.1.2 on 2021-10-17 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='nameEmail',
            field=models.CharField(db_column='nameEmail', blank=True, null=True, editable=False, max_length=255, verbose_name='label'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contact',
            name='person',
            field=models.CharField(blank=True, null=True, editable=False, max_length=255, verbose_name='full name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='octopusaccount',
            name='name',
            field=models.CharField(blank=True, null=True, editable=False, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='alt_name',
            field=models.CharField(blank=True, null=True, editable=False, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(blank=True, null=True, editable=False, max_length=255),
            preserve_default=False,
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS new_octopusAccount;"
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS update_octopusAccount;"
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS new_agency_post;"
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS update_agency_post;"
        ),
        migrations.RunSQL(
            "DROP TRIGGER IF EXISTS update_organisation;"
        ),
    ]
