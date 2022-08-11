import utils

async def on_admin_command(self, message):
	await message.delete()
	await message.channel.send("Channel unlocked!")
	await utils.channel.unlock(message.channel)