# Generated by Django 3.0.7 on 2020-11-07 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_chat_chatroom'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='send_to',
        ),
        migrations.AddField(
            model_name='chatroom',
            name='user1',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user1', to='user.CustomerUser'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='user2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user2', to='user.CustomerUser'),
        ),
    ]
