# Generated by Django 5.1.6 on 2025-02-07 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(db_index=True, max_length=20)),
                ('symbol', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProviderClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('api_url', models.URLField(help_text='API URL of the provider')),
                ('encrypted_api_key', models.TextField()),
                ('priority', models.PositiveIntegerField(default=1, help_text='lower the number means higher priority')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valuation_date', models.DateField(db_index=True)),
                ('rate_value', models.DecimalField(db_index=True, decimal_places=6, max_digits=10)),
                ('exchanged_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='currencyapp.currency')),
                ('source_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchanges', to='currencyapp.currency')),
            ],
        ),
    ]
