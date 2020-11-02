# Generated by Django 3.0.7 on 2020-11-02 04:56

import datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user', '0017_auto_20201030_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_comment', models.DateField(default=datetime.datetime.today)),
                ('comment', models.TextField()),
                ('comment_done_by', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('product', models.ManyToManyField(to='user.Products')),
            ],
        ),
    ]
