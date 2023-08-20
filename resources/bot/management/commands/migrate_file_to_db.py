# Standard imports
import os
# Extra imports
import hashlib
import shutil
# Django imports
from django.core.management.base import BaseCommand
# Project imports
from resources.audio.models import AudioInEntity, AudioInServer, Audio
from resources.entity.models import Entity
from resources.server.models import Server


class Command(BaseCommand):

    def handle(self, *args, **options):

        print("Migrate files to db...\n")

        absolute_path = "/mnt/c/Users/facub/Desktop/Apagar/audio/"
        dest_path = "/mnt/c/Users/facub/Desktop/Apagar/wavu/audios/"

        for root, dirs, files in os.walk(absolute_path):
            discord_id = root
            if absolute_path in discord_id:
                discord_id = discord_id.replace(absolute_path, '')
            else:
                continue

            if not discord_id:
                continue

            entity_id = 0

            try:
                if '/' in discord_id:
                    splitted = discord_id.split("/")
                    server_id = int(splitted[0])
                    entity_id = int(splitted[1])
                else:
                    server_id = int(discord_id)
            except ValueError:
                print("This directory is not a server or entity id")
                continue

            server, _ = Server.objects.get_or_create(discord_id=server_id)

            if entity_id:
                entity, _ = Entity.objects.get_or_create(discord_id=entity_id, server=server)

                obj = AudioInEntity
                query = {"entity": entity}
            else:
                obj = AudioInServer
                query = {"server": server}

            for file in files:
                path = f"{root}/{file}"
                hashcode = hashlib.md5(open(path, 'rb').read()).hexdigest()
                audio, created = Audio.objects.get_or_create(hashcode=hashcode)
                if created and not os.path.exists(f"{dest_path}/{hashcode}.mp3"):
                    obj.objects.create(**query, audio=audio, name=file.split(".mp3")[0])
                    shutil.copyfile(path, f"{dest_path}/{hashcode}.mp3")

        print("")
        print("Migrated complited")
