# Generated by Django 3.1.2 on 2022-07-21 08:35

from django.db import migrations, models

def split_onregister_field(apps, schema_editor):
    """
    initialise split up onRegister fields
    """
    ContactOrganisation = apps.get_model('contacts', 'contactorganisation')
    count = ContactOrganisation.objects.update(
        emailOnRegister=models.F('onRegister'),
        nameOnRegister=models.F('onRegister'),
        phoneOnRegister=models.F('onRegister')
    )
    print(f"updated: {count}")

class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_convert_phone_numbers'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactorganisation',
            name='emailOnRegister',
            field=models.BooleanField(db_column='emailOnRegister', default=False, verbose_name='email on Register?'),
        ),
        migrations.AddField(
            model_name='contactorganisation',
            name='nameOnRegister',
            field=models.BooleanField(db_column='nameOnRegister', default=False, verbose_name='name on Register?'),
        ),
        migrations.AddField(
            model_name='contactorganisation',
            name='phoneOnRegister',
            field=models.BooleanField(db_column='phoneOnRegister', default=False, verbose_name='phone on Register?'),
        ),
        migrations.RunPython(split_onregister_field),
        migrations.RemoveField(
            model_name='contactorganisation',
            name='onRegister',
        ),
    ]
