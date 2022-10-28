import discord
import utils

async def on_admin_command(self, message):
	channel = message.channel
	args = utils.channel.get_args(message)

	if len(args) < 2:
		await channel.send("{0}, the format is: describe <user/hex> - gets the identifiers of a Discord user or vise versa".format(message.author.mention))
		return
	
	selects = "id, steam, name, discord, flags, priority, first_joined, last_played"

	if not await utils.db.get_target(message.mentions, args[1], message, selects):
		return

	for (id, identifier, name, user, flags, priority, first_joined, last_played) in utils.db.cur:
		user_mention = None
		if user is None:
			user_mention = "*Unknown*"
		else:
			user_mention = f"<@!{user}>"
		embed = discord.Embed(title="", description=user_mention)
		embed.add_field(name="Identifiers", value=f"ID: {id}\nDiscord: {user}\nSteam: {identifier}", inline=False)
		embed.add_field(name="Name", value=name, inline=False)
		embed.add_field(name="Flags", value=flags, inline=True)
		embed.add_field(name="Priority", value=priority, inline=True)
		embed.add_field(name="Stats", value=f"Last Played: {last_played}\nFirst Joined: {first_joined}", inline=False)

		await message.delete()
		await channel.send(embed=embed)
		return