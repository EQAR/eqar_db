# Generated by Django 3.1.2 on 2021-10-17 21:06

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
                ('id', models.AutoField(db_column='cid', primary_key=True, serialize=False, verbose_name='Contact ID')),
                ('firstName', models.CharField(blank=True, db_column='firstName', max_length=255, null=True, verbose_name='first name')),
                ('lastName', models.CharField(blank=True, db_column='lastName', max_length=255, null=True, verbose_name='last name')),
                ('person', models.CharField(editable=False, max_length=255)),
                ('nameEmail', models.CharField(db_column='nameEmail', editable=False, max_length=255)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True, verbose_name='email address')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='phone (landline)')),
                ('mobile', models.CharField(blank=True, max_length=255, null=True, verbose_name='phone (mobile)')),
                ('brussels', models.BooleanField(default=False, verbose_name='Brussels-based')),
                ('postal', models.BooleanField(default=False, verbose_name='receive paper mail')),
                ('addressExtension', models.CharField(blank=True, db_column='addressExtension', max_length=255, null=True, verbose_name='address extension')),
                ('address1', models.CharField(blank=True, help_text='Insert only if different from organisation!', max_length=255, null=True)),
                ('address2', models.CharField(blank=True, max_length=255, null=True)),
                ('postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
            ],
            options={
                'verbose_name': 'person',
                'db_table': 'contact',
                'ordering': ['lastName', 'firstName'],
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('iso3', models.CharField(max_length=3, primary_key=True, serialize=False, verbose_name='ISO 3166-1 alpha-3 code')),
                ('iso2', models.CharField(blank=True, max_length=2, null=True, unique=True, verbose_name='ISO 3166-1 alpha-2 code')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (English)')),
                ('name_local', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (local language)')),
                ('longname', models.CharField(blank=True, max_length=255, null=True, verbose_name='long name (English)')),
                ('longname_local', models.CharField(blank=True, max_length=255, null=True, verbose_name='long name (local language)')),
                ('tableau_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (for Tableau)')),
                ('infogram_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='name (for Infogram)')),
                ('capital', models.CharField(blank=True, max_length=255, null=True)),
                ('tldomain', models.CharField(blank=True, max_length=2, null=True, verbose_name='top-level domain')),
                ('phone_prefix', models.CharField(blank=True, max_length=5, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('ehea', models.BooleanField(default=False, verbose_name='EHEA member')),
                ('eu', models.BooleanField(default=False, verbose_name='EU member')),
                ('eter', models.BooleanField(default=False, verbose_name='covered by ETER')),
                ('typo3boxdata', models.IntegerField(blank=True, null=True, verbose_name='Typo3 data')),
            ],
            options={
                'verbose_name_plural': 'countries',
                'db_table': 'country',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False, verbose_name='ISO 639-1 code')),
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
                ('id', models.IntegerField(db_column='rid', primary_key=True, serialize=False, verbose_name='Role ID')),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'organisation type',
                'db_table': 'role',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(db_column='oid', primary_key=True, serialize=False, verbose_name='Organisation ID')),
                ('longname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('acronym', models.CharField(blank=True, max_length=15, null=True, verbose_name='Acronym')),
                ('name', models.CharField(editable=False, max_length=255)),
                ('alt_name', models.CharField(editable=False, max_length=255)),
                ('address1', models.CharField(blank=True, max_length=255, null=True, verbose_name='Address')),
                ('address2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Address (2)')),
                ('postcode', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
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
                ('id', models.AutoField(db_column='oaid', primary_key=True, serialize=False, verbose_name='ID')),
                ('octopusId', models.IntegerField(db_column='octopusId', unique=True, verbose_name='Octopus relation ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('contact', models.CharField(blank=True, max_length=255, null=True)),
                ('client', models.BooleanField(default=False)),
                ('supplier', models.BooleanField(default=False)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('cid', models.ForeignKey(blank=True, db_column='cid', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.CASCADE, to='contacts.organisation')),
            ],
            options={
                'verbose_name': 'financial account',
                'db_table': 'octopusAccount',
            },
        ),
        migrations.CreateModel(
            name='DeqarPartner',
            fields=[
                ('id', models.AutoField(db_column='pid', primary_key=True, serialize=False, verbose_name='Partner ID')),
                ('pic', models.IntegerField(blank=True, null=True, verbose_name='EU PIC')),
                ('pic_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Official name (PIC)')),
                ('type', uni_db.fields.EnumField(choices=[('Coordinator', 'Coordinator'), ('Stakeholder Partner', 'Stakeholder Partner'), ('QAA Partner', 'QAA Partner'), ('Research Centre', 'Research Centre'), ('Associate Partner', 'Associate Partner')], verbose_name='Role')),
                ('signatory_name', models.CharField(blank=True, max_length=255, null=True)),
                ('expenditure', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('max_contrib', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='max. EU grant')),
                ('prog_report_expected', models.DateField(blank=True, null=True, verbose_name='progress report expected by')),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('manager', models.ForeignKey(blank=True, db_column='manager', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_manager', to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
                ('signatory', models.ForeignKey(blank=True, db_column='signatory', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_sign', to='contacts.contact')),
                ('technician', models.ForeignKey(blank=True, db_column='technician', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar1_tech', to='contacts.contact')),
            ],
            options={
                'verbose_name': 'DEQAR project partner',
                'db_table': 'deqarPartner',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='DeqarConnectPartner',
            fields=[
                ('id', models.AutoField(db_column='pid', primary_key=True, serialize=False, verbose_name='Partner ID')),
                ('pic', models.IntegerField(blank=True, null=True, verbose_name='EU PIC')),
                ('type', uni_db.fields.EnumField(choices=[('Coordinator', 'Coordinator'), ('QAA', 'QAA'), ('ENIC-NARIC', 'ENIC-NARIC'), ('Associate', 'Associate'), ('Expert', 'Expert')], verbose_name='Role')),
                ('notes', models.TextField(blank=True, null=True)),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('contact_admin', models.ForeignKey(blank=True, db_column='contact_admin', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar_connect_admin', to='contacts.contact')),
                ('contact_technical', models.ForeignKey(blank=True, db_column='contact_technical', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deqar_connect_tech', to='contacts.contact')),
                ('organisation', models.OneToOneField(db_column='oid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.organisation')),
            ],
            options={
                'verbose_name': 'DEQAR CONNECT partner',
                'db_table': 'deqarConnectPartner',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ContactOrganisation',
            fields=[
                ('id', models.AutoField(db_column='coid', primary_key=True, serialize=False, verbose_name='ID')),
                ('sendOfficial', models.BooleanField(db_column='sendOfficial', default=False)),
                ('sendDeqar', models.BooleanField(db_column='sendDeqar', default=False)),
                ('sendInvoice', models.BooleanField(db_column='sendInvoice', default=False)),
                ('function', models.CharField(blank=True, max_length=255, null=True)),
                ('mtime', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(db_column='cid', on_delete=django.db.models.deletion.RESTRICT, to='contacts.contact')),
                ('organisation', models.ForeignKey(db_column='oid', on_delete=django.db.models.deletion.CASCADE, to='contacts.organisation')),
            ],
            options={
                'verbose_name': 'contact person',
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
            name='prefLang',
            field=models.ForeignKey(db_column='prefLang', default='en', on_delete=django.db.models.deletion.RESTRICT, to='contacts.language', verbose_name='language preference'),
        ),
    ]
