# Generated by Django 3.1.2 on 2020-10-13 20:31

from django.db import migrations, models
import django.db.models.deletion
import uni_db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(db_column='cid', primary_key=True, serialize=False)),
                ('firstname', models.CharField(blank=True, db_column='firstName', max_length=255, null=True)),
                ('lastname', models.CharField(blank=True, db_column='lastName', max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('mobile', models.CharField(blank=True, max_length=255, null=True)),
                ('brussels', models.BooleanField(default=False)),
                ('postal', models.BooleanField(default=False)),
                ('address_extension', models.CharField(blank=True, db_column='addressExtension', max_length=255, null=True)),
                ('address1', models.CharField(blank=True, max_length=255, null=True)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'contact',
                'ordering': ['lastname'],
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('iso3', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('iso2', models.CharField(blank=True, max_length=2, null=True, unique=True)),
                ('longname', models.CharField(blank=True, max_length=255, null=True)),
                ('longname_local', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('name_local', models.CharField(blank=True, max_length=255, null=True)),
                ('tableau_name', models.CharField(blank=True, max_length=255, null=True)),
                ('infogram_name', models.CharField(blank=True, max_length=255, null=True)),
                ('capital', models.CharField(blank=True, max_length=255, null=True)),
                ('tldomain', models.CharField(blank=True, max_length=2, null=True)),
                ('phone_prefix', models.CharField(blank=True, max_length=5, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('ehea', models.IntegerField()),
                ('eu', models.IntegerField()),
                ('eter', models.IntegerField()),
                ('typo3boxdata', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'country',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('language', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'language',
                'ordering': ['language'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.IntegerField(db_column='rid', primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'role',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(db_column='oid', primary_key=True, serialize=False)),
                ('longname', models.CharField(blank=True, max_length=255, null=True)),
                ('acronym', models.CharField(blank=True, max_length=15, null=True)),
                ('address1', models.CharField(blank=True, max_length=255, null=True)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(blank=True, db_column='country', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.country', to_field='iso2')),
                ('role', models.ForeignKey(db_column='role', on_delete=django.db.models.deletion.DO_NOTHING, to='contacts.role')),
            ],
            options={
                'db_table': 'organisation',
                'ordering': ['longname'],
            },
        ),
        migrations.CreateModel(
            name='OctopusAccount',
            fields=[
                ('id', models.AutoField(db_column='oaid', primary_key=True, serialize=False)),
                ('octopus_id', models.IntegerField(db_column='octopusId', unique=True)),
                ('contact', models.CharField(blank=True, max_length=255, null=True)),
                ('client', models.BooleanField(default=False)),
                ('supplier', models.BooleanField(default=False)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('cid', models.ForeignKey(blank=True, db_column='cid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.CASCADE, to='contacts.organisation')),
            ],
            options={
                'db_table': 'octopusAccount',
            },
        ),
        migrations.CreateModel(
            name='DeqarPartner',
            fields=[
                ('id', models.AutoField(db_column='pid', primary_key=True, serialize=False)),
                ('pic', models.IntegerField(blank=True, null=True)),
                ('pic_name', models.CharField(blank=True, max_length=255, null=True)),
                ('type', uni_db.fields.EnumField(choices=[('Coordinator', 'Coordinator'), ('Stakeholder Partner', 'Stakeholder Partner'), ('QAA Partner', 'QAA Partner'), ('Research Centre', 'Research Centre'), ('Associate Partner', 'Associate Partner')], default='Coordinator')),
                ('signatory_name', models.CharField(blank=True, max_length=255, null=True)),
                ('expenditure', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('max_contrib', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('prog_report_expected', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('manager', models.ForeignKey(blank=True, db_column='manager', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_manager', to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
                ('signatory', models.ForeignKey(blank=True, db_column='signatory', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_sign', to='contacts.contact')),
                ('technician', models.ForeignKey(blank=True, db_column='technician', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_tech', to='contacts.contact')),
            ],
            options={
                'db_table': 'deqarPartner',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='DeqarConnectPartner',
            fields=[
                ('id', models.AutoField(db_column='pid', primary_key=True, serialize=False)),
                ('pic', models.IntegerField(blank=True, null=True)),
                ('type', uni_db.fields.EnumField(choices=[('Coordinator', 'Coordinator'), ('QAA', 'QAA'), ('ENIC-NARIC', 'ENIC-NARIC'), ('Associate', 'Associate'), ('Expert', 'Expert')], default='Coordinator')),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('contact_admin', models.ForeignKey(blank=True, db_column='contact_admin', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar_connect_admin', to='contacts.contact')),
                ('contact_technical', models.ForeignKey(blank=True, db_column='contact_technical', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar_connect_tech', to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
            ],
            options={
                'db_table': 'deqarConnectPartner',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ContactOrganisation',
            fields=[
                ('id', models.AutoField(db_column='coid', primary_key=True, serialize=False)),
                ('sendofficial', models.BooleanField(db_column='sendOfficial', default=False)),
                ('senddeqar', models.BooleanField(db_column='sendDeqar', default=False)),
                ('sendinvoice', models.BooleanField(db_column='sendInvoice', default=False)),
                ('function', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(db_column='cid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.contact')),
                ('organisation', models.ForeignKey(db_column='oid', on_delete=django.db.models.deletion.CASCADE, to='contacts.organisation')),
            ],
            options={
                'db_table': 'contact_organisation',
                'ordering': ['function'],
                'unique_together': {('organisation', 'contact')},
            },
        ),
        migrations.AddField(
            model_name='contact',
            name='country',
            field=models.ForeignKey(blank=True, db_column='country', null=True, on_delete=django.db.models.deletion.RESTRICT, to='contacts.country', to_field='iso2'),
        ),
        migrations.AddField(
            model_name='contact',
            name='organisation',
            field=models.ManyToManyField(through='contacts.ContactOrganisation', to='contacts.Organisation'),
        ),
        migrations.AddField(
            model_name='contact',
            name='pref_lang',
            field=models.ForeignKey(db_column='prefLang', on_delete=django.db.models.deletion.RESTRICT, to='contacts.language'),
        ),
    ]
