# Generated by Django 3.1.2 on 2022-08-29 16:25

from django.db import migrations, models
import django.db.models.deletion
import uni_db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0005_prevent_empty_organisation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='panel_2_1',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.1 panel/rapporteurs/RC'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_2',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.2'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_3',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.3'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_4',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.4'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_5',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.5'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_6',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.6'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_2_7',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 2.7'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_1',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.1'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_2',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.2'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_3',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.3'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_4',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.4'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_5',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.5'),
        ),
        migrations.AlterField(
            model_name='applications',
            name='panel_3_6',
            field=uni_db.fields.EnumField(blank=True, choices=[('Compliance', 'Compliance'), ('Full compliance', 'Full compliance'), ('Substantial compliance', 'Substantial compliance'), ('Partial compliance', 'Partial compliance'), ('Non-compliance', 'Non-compliance')], null=True, verbose_name='ESG 3.6'),
        ),
    ]
