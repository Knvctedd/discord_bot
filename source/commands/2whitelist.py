import discord
import utils

async def on_admin_command(self, message):
	channel = message.channel

	for target in message.mentions:
		did_exist = False
		utils.db.cur.execute("SELECT SUBSTRING_INDEX(identifier, ':', -1) FROM users WHERE discord=CONCAT('discord:', %s)", (target.id,))

		# Get the result
		for (identifier,) in utils.db.cur:
			setters = f"steam='{identifier}', discord='{target.id}'"

			# Update the user
			utils.db.dev_cur.execute(f"INSERT IGNORE INTO users SET {setters} ON DUPLICATE KEY UPDATE {setters}, priority=GREATEST(priority, 0)")
			utils.db.dev_conn.commit()

			# Send message
			embed = discord.Embed(title="Development Server", description=f"{target.mention} has been whitelisted!", colour=discord.Colour.gold())
			embed.add_field(name="Whitelisted", value=message.author.mention, inline=True)
			embed.add_field(name="Identifier", value=identifier, inline=False)

			await channel.send(embed=embed)

			did_exist = True

		# Add them to the whitelist
		if not did_exist:
			await channel.send("They haven't joined the live server yet!")

	await message.delete()