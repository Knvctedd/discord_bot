import utils

async def on_admin_command(self, message):
	await message.delete()
	await message.channel.send("Channel locked!")
	await utils.channel.lock(message.channel)