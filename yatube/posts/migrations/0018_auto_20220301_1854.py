# Generated by Django 2.2.16 on 2022-03-01 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20220301_1845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'posts_1', 'ordering': ['-pub_date']},
        ),
    ]