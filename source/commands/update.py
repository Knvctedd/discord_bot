import discord
import utils

async def on_admin_command(self, message):
	channel = message.channel
	count = 0

	await message.delete()

	for user in message.guild.members:
		count += 1
		await utils.twitch.update_streamer_role(self, user, message.guild)
	
	await channel.send(f"Updated {count} members!")