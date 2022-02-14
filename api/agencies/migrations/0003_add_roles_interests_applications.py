# Generated by Django 3.1.2 on 2022-02-04 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_remove_language'),
        ('agencies', '0002_drop_virtual_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='applications',
            name='interests',
            field=models.ManyToManyField(related_name='application_interest', through='agencies.ApplicationInterest', to='contacts.Contact'),
        ),
        migrations.AddField(
            model_name='applications',
            name='roles',
            field=models.ManyToManyField(related_name='application_role', through='agencies.ApplicationRole', to='contacts.Contact'),
        ),
    ]