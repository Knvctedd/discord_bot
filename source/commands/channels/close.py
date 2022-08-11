import discord
import tickets
import utils

async def on_admin_command(self, message):
	channel = message.channel
	name = channel.name
	
	reason = message.content[len(";close"):len(message.content)]
	if reason == "":
		reason = None
	else:
		reason = reason[1:len(reason)]

	author = await tickets.close(channel, reason)
	
	if author is not None:
		try:
			await author.send(f"{name} has been closed ({reason or 'No reason specified.'})")
		except:
			print(f"Couldn't message {author.name}#{author.discriminator} about {name}")