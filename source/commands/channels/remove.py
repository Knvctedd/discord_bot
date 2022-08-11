import discord

async def on_admin_command(self, message):
	channel = message.channel
	target = message.mentions

	if type(target) is list and len(target) > 0:
		target = target[0]
	else:
		target = None
	
	if target is None:
		await channel.send(f"User not found, {message.author.mention}!")
		return
	
	await channel.set_permissions(target, overwrite=None)
	await channel.send(f"Removed {target.mention}!")