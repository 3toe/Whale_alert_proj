# Generated by Django 2.2 on 2022-01-06 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='faved_by',
            field=models.ManyToManyField(related_name='fav_currency', to='main.User'),
        ),
    ]
