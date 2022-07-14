# Generated by Django 3.1.2 on 2022-05-11 15:49

from django.db import migrations

import phonenumbers

def convert_phone_numbers(apps, schema_editor):
    Contact = apps.get_model('contacts', 'contact')
    for contact in Contact.objects.iterator():
        is_changed = False
        if contact.phone:
            try:
                phone_parsed = phonenumbers.parse(contact.phone, 'BE')
                contact.phone = phonenumbers.format_number(phone_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                is_changed = True
            except phonenumbers.phonenumberutil.NumberParseException:
                pass
        if contact.mobile:
            try:
                mobile_parsed = phonenumbers.parse(contact.mobile, 'BE')
                contact.mobile = phonenumbers.format_number(mobile_parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                is_changed = True
            except phonenumbers.phonenumberutil.NumberParseException:
                pass
        if is_changed:
            contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_fix_sorting'),
    ]

    operations = [
        migrations.RunPython(convert_phone_numbers),
    ]

