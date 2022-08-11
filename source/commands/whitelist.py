import discord
import re
import tickets
import utils

async def on_admin_command(self, message):
	channel = message.channel
	args = utils.channel.get_args(message)

	if len(args) < 3:
		await channel.send("{0}, the format is: whitelist <user> <hex>".format(message.author.mention))
		return
	
	target = message.mentions
	if type(target) is list and len(target) > 0:
		target = target[0]
	else:
		target = None

	steam = args[2].lower()

	# Check name
	if target is None:
		await channel.send("User not found!")
		return
	
	# Convert prefixed hexes
	if steam.startswith("steam:"):
		steam = steam[6:len(steam)]

	# Check hex
	if len(steam) != 15:
		await channel.send("Invalid hex!")
		return
	
	channel = discord.utils.get(message.guild.text_channels, name="whitelisting")

	if channel is None:
		print("Whitelisting channel not found!")
		channel = message.channel

	# Find if they exist
	utils.db.cur.execute("SELECT id, discord FROM users WHERE identifier=CONCAT('steam:', %s)", (steam,))

	had_user = False

	embed = discord.Embed(title="", description=f"{target.mention} has been whitelisted!", colour=discord.Colour.gold())

	# Get the result
	for (userId, user) in utils.db.cur:
		if user is not None:
			embed.add_field(name="Overriding", value=f"<@!{user[8:len(user)]}>")
		
		# Update the user
		utils.db.cur.execute("UPDATE users SET priority=GREATEST(priority, 0), discord=CONCAT('discord:', %s) WHERE identifier=CONCAT('steam:', %s)", (target.id, steam,))
		utils.db.conn.commit()

		had_user = True

		break

	# Send message
	embed.add_field(name="Whitelisted", value=message.author.mention, inline=True)

	if tickets.is_ticket(message.channel):
		embed.add_field(name="Application", value=re.sub("(^.+\\-)(.+)", "\\2", message.channel.name), inline=True)
	
	embed.add_field(name="Identifier", value="steam:" + steam, inline=False)

	await channel.send(embed=embed)

	if channel != message.channel:
		await message.channel.send(f"> {target.mention}, welcome to NonstopRP!\n\n> Thank you for applying to our exclusive whitelist! You may now play by connecting to `play.nonstoprp.net`!\n\n> Please keep in mind that your whitelisted status may be removed at any point at the discretion of our staff team. Make sure you have read and understand the rules.")

	# Add them to the whitelist
	if not had_user:
		utils.db.cur.execute("INSERT INTO users SET identifier=CONCAT('steam:', %s), discord=CONCAT('discord:', %s)", (steam, target.id,))
		utils.db.conn.commit()
	
	# Add role to target
	role = discord.utils.get(message.guild.roles, name="Whitelisted")
	
	try:
		await target.add_roles(role, reason="Whitelist", atomic=True)
	except discord.HTTPException:
		print("HTTP exception")
		pass
	
	await message.delete()