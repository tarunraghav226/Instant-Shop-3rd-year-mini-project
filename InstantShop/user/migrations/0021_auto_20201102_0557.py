# Generated by Django 3.0.7 on 2020-11-02 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_comment_productcomments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomments',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user.Products'),
        ),
    ]
