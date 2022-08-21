import discord
import utils
import time

waitingFor = 0
query_queue = []

async def on_admin_command(self, message):
	global waitingFor
	global query_queue

	channel = message.channel
	waitingFor = message.author.id

	await message.delete()

	utils.db.cur.execute("SELECT steam, discord, first_joined, last_played FROM users WHERE `priority` >= -127 AND `discord` IS NOT NULL")
	total = 0
	totalLeft = 0
	totalLeftRecent = 0
	totalNeverJoined = 0

	print("To remove from whitelist:")

	for (steam, _discord, first_joined, last_played) in utils.db.cur:
		total += 1
		user_id = int(_discord)

		if channel.guild.get_member(user_id) is None:
			# await channel.send(f"<@{user_id}>")
			if first_joined is None:
				totalNeverJoined += 1
			elif last_played is not None and last_played.timestamp() * 1000 > int(round(time.time() * 1000)) - 1000 * 60 * 60 * 24 * 7:
				totalLeftRecent += 1
			print(f"steam:{steam}, discord:{_discord}")
			query_queue.append(f"UPDATE `users` SET `priority`=-128 WHERE `steam`='{steam}' AND `discord`='{_discord}'")
			totalLeft += 1
	
	embed = discord.Embed(title="")
	embed.add_field(name="Whitelisted", value=f"{total} users", inline=False)
	embed.add_field(name="Inactive", value=f"{totalLeft} users\n{totalLeftRecent} users joined within 7 days", inline=False)
	embed.add_field(name="Never Joined", value=f"{totalNeverJoined} users", inline=False)
	embed.set_footer(text="Check console for a user dump!\n\nType 'confirm' to unwhitelist users that have left the Discord.")

	await channel.send("", embed=embed)

async def on_message(self, message):
	global waitingFor
	global query_queue

	if waitingFor == 0 or message.author.id != waitingFor or message.content != "confirm":
		return

	channel = message.channel

	for query in query_queue:
		utils.db.cur.execute(query)
		utils.db.conn.commit()

	embed = discord.Embed(title="")
	embed.add_field(name="Invoked By", value=message.author.mention)
	embed.add_field(name="Removed Whitelist", value=f"{len(query_queue)} users", inline=False)

	waitingFor = 0
	query_queue = []

	await channel.send(embed=embed)
	await message.delete()