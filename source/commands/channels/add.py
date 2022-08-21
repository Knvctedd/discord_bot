import discord
import utils

async def on_admin_command(self, message):
	channel = message.channel
	args = utils.channel.get_args(message)
	target = None

	if not await utils.db.get_target(message.mentions, args[1], message, "discord"):
		return

	for (user,) in utils.db.cur:
		if user is not None:
			target = channel.guild.get_member(int(user))

	if target is None:
		await channel.send(f"User not found, {message.author.mention}!")
		return
	
	await message.delete()
	await to(target, channel)
	await channel.send(f"Added {target.mention}!")

async def to(user, channel):
	overwrite = discord.PermissionOverwrite()
	overwrite.attach_files = True
	overwrite.embed_links = True
	overwrite.read_message_history = True
	overwrite.read_messages = True
	overwrite.send_messages = True
	
	await channel.set_permissions(user, overwrite=overwrite)