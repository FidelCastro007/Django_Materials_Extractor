# Generated by Django 5.1.3 on 2024-12-13 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='byproduct',
            name='quality',
            field=models.CharField(default='Medium', max_length=10),
        ),
    ]