# Generated by Django 2.2.9 on 2022-07-25 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220724_2022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(unique=True),
        ),
    ]