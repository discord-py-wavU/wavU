# Generated by Django 4.1.2 on 2022-10-23 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("server", "0002_alter_server_discord_id"),
        ("entity", "0002_alter_entity_discord_id"),
    ]

    operations = [
        migrations.RemoveField(model_name="entity", name="server"),
        migrations.AddField(
            model_name="entity",
            name="server",
            field=models.ManyToManyField(related_name="entities", to="server.server"),
        ),
    ]