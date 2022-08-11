import re

async def lock(channel):
	for member in channel.members:
		if member in channel.overwrites:
			overwrite = discord.PermissionOverwrite()
			overwrite.attach_files = False
			overwrite.embed_links = False
			overwrite.read_message_history = True
			overwrite.read_messages = True
			overwrite.send_messages = False
			
			await channel.set_permissions(member, overwrite=overwrite)

async def unlock(channel):
	for member in channel.members:
		if member in channel.overwrites:
			overwrite = discord.PermissionOverwrite()
			overwrite.attach_files = True
			overwrite.embed_links = True
			overwrite.read_message_history = True
			overwrite.read_messages = True
			overwrite.send_messages = True
			
			await channel.set_permissions(member, overwrite=overwrite)

def get_args(message):
	content = re.sub("^\s", "", re.sub("\ +", " ", message.content))
	return content[1:len(content)].split(" ")