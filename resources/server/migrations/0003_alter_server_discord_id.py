# Generated by Django 4.1.2 on 2022-11-01 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("server", "0002_alter_server_discord_id")]

    operations = [
        migrations.AlterField(
            model_name="server",
            name="discord_id",
            field=models.BigIntegerField(db_index=True, default=0),
        )
    ]