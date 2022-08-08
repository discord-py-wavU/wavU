import discord

'''
token = 'Mzc5MTU4Nzc0MTU5NTA3NDU5.WgftIA.e3bzfTVkYxaxGcVpK52NGI3Enp0'  # wavU
prefix = '='
status = discord.Status.online
game = prefix + 'help'
path = '/app/audio'  # docker path
'''

token = "ODAzMzExODc1NDQxODE5NzA5.YA78ew.60BLW2Zp-xT3VOV5R_gP2ZSdbjc"
prefix = "_"
status = discord.Status.online
game = prefix + "help"
path = "/mnt/c/Users/facub/OneDrive/Documentos/GitHub/wavU/audio"


'''
docker build -t wavu .
docker run -d -v c:/Users/facub/OneDrive/Escritorio/Apagar/audio:/app/audio
'''