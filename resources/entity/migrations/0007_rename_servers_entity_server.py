# Generated by Django 4.1.2 on 2022-11-04 01:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("entity", "0006_remove_entity_servers_entity_servers")]

    operations = [
        migrations.RenameField(
            model_name="entity", old_name="servers", new_name="server"
        )
    ]
