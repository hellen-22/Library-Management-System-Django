# Generated by Django 5.0.1 on 2024-02-02 15:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='borrowing_fee',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=10, validators=[django.core.validators.MinValueValidator(1.0)]),
        ),
    ]
