import discord
import utils

async def on_admin_command(self, message):
	await message.delete()

	embed = discord.Embed(description="Unfortunately we are dismissing this report as it does not meet our guidelines.")
	embed.set_footer(text="Please do not open further tickets or reports regarding this situation unless asked to do so.")
	
	reason = message.content[len(";dismiss"):len(message.content)]

	if reason != "":
		embed.add_field(name="Reason", value=reason)

	await message.channel.send(embed=embed)
	await utils.channel.lock(message.channel)