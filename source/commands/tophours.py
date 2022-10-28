import discord
import math
import utils

async def on_admin_command(self, message):
	channel = message.channel
	args = utils.channel.get_args(message)

	if len(args) < 2:
		await channel.send("{0}, the format is: describe <user/hex> - gets the identifiers of a Discord user or vise versa".format(message.author.mention))
		return
	
	selects = "id, discord"

	if not await utils.db.get_target(message.mentions, args[1], message, selects):
		return
	
	await message.delete()

	result = utils.db.cur.fetchone()
	user_id = None
	user = None

	if result is None or len(result) < 2:
		return
	else:
		user_id = result[0]
		user = result[1]

	utils.db.cur.execute("SELECT id, user_id, first_name, last_name, dob, gender, bank, time_played, dead FROM characters WHERE user_id=?", (user_id,))

	embed = discord.Embed(title=f"Characters (User {user_id})", description="", colour=discord.Colour.green())

	total_time_played = 0.0

	for (character_id, user_id, first_name, last_name, dob, gender, bank, time_played, dead) in utils.db.cur:
		# user_mention = None
		# if user is None:
		# 	user_mention = "*Unknown*"
		# else:
		# 	user_mention = f"<@!{user[8:len(user)]}>"
		
		total_time_played = total_time_played + time_played

		value = f"Gender: {gender}\nTime Played: {math.floor(time_played / 3600)} hours"

		if dead == b'\x01':
			value = value + "\n*Deceased*"

		embed.add_field(name=f"{first_name} {last_name} ({character_id})", value=value)
	
	embed.description = f"<@!{user}>\n\nTime Played: {math.floor(total_time_played / 3600)} hours"
	
	await channel.send(embed=embed)