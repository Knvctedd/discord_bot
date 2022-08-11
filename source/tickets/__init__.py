# Imported Modules
import datetime
import discord
import io
import os
import re
import sys

from datetime import datetime
from datetime import timedelta

# Color Modules
from colorama import init
from termcolor import colored

init(autoreset=True)

# Custom Modules
import __main__
import tickets.options
import tickets.templates as templates
import commands

options = tickets.options.options
submit_channel_name = "submit-ticket"
transcript_channel_name = "ticket-transcripts"
ticket_count = 0
cooldowns = {}
is_dev = "enable_dev" in sys.argv

# Definitions
async def on_ready(self, guild):
	if not is_dev:
		try:
			with io.open(f"{os.getcwd()}/ticket_count.txt", "r") as f:
				tickets.ticket_count = int(f.read())
		except:
			pass

	await init_guild(self, guild)

	# test = discord.utils.get(guild.channels, id=770506784187088976)
	# await save_transcript(test)

# async def on_guild_channel_create(self, channel):
# 	if len(re.findall("ticket\-", channel.name, flags=re.I)) > 0:
# 		await init_channel(channel)

async def on_raw_reaction_add(self, payload):
	user = payload.member
	user_id = payload.user_id

	if user_id == self.user.id:
		return

	try:
		guild = discord.utils.get(self.guilds, id=payload.guild_id)
		channel = discord.utils.get(guild.channels, id=payload.channel_id)
		message = await channel.history().get(id=payload.message_id)
	except:
		return

	if message is None or message.author is None or message.author.id != self.user.id or channel.name != submit_channel_name:
		return
	
	await message.remove_reaction(payload.emoji, user)

	now = datetime.now()
	if not cooldowns.get(user_id) is None and now < cooldowns.get(user_id) + timedelta(minutes=1):
		return
	
	cooldowns[user_id] = now

	for option in options:
		if option.get("emoji") == payload.emoji.name:
			category = discord.utils.get(guild.categories, name=option.get("category") or "Support")
			if not category:
				print(f"{guild} is missing a Support category!")
				return

			extra = ""
			if "ticket_name" in option:
				extra = option.get("ticket_name") + "-"
			
			tickets.ticket_count = tickets.ticket_count + 1
			target_channel = await guild.create_text_channel(f"ticket-{extra}{tickets.ticket_count}", category=category)
			title = option.get("title")

			support_role = discord.utils.get(guild.roles, name="Support Team")
			# staff_role = discord.utils.get(guild.roles, name="Staff Team")

			if title == "Player Report":
				await target_channel.edit(slowmode_delay=60)

				discuss_category = discord.utils.get(guild.categories, name="Reports Discussion")
				discuss_channel = await guild.create_text_channel(f"ticket-discussion-{tickets.ticket_count}", category=discuss_category)

				overwrite = discord.PermissionOverwrite()
				overwrite.send_messages = True
				overwrite.read_messages = True
				overwrite.read_message_history = True

				await target_channel.set_permissions(support_role, overwrite=overwrite)

				discuss_message = await send_template(discuss_channel, "", "Discussion", templates.player_report_discussion, None)
				await discuss_message.add_reaction("💬")
			elif title == "Contact Management":
				management_role = discord.utils.get(guild.roles, name="Management")

				overwrite = discord.PermissionOverwrite()
				overwrite.send_messages = False
				overwrite.read_messages = False
				overwrite.read_message_history = False

				await target_channel.set_permissions(support_role, overwrite=overwrite)

				overwrite.send_messages = True
				overwrite.read_messages = True
				overwrite.read_message_history = True

				await target_channel.set_permissions(management_role, overwrite=overwrite)

			await send_template(target_channel, user, title, option.get("description"), option.get("fields"))
			await commands.channels.add.to(user, target_channel)

			if not is_dev:
				with io.open(f"{os.getcwd()}/ticket_count.txt", "w") as f:
					f.write(str(tickets.ticket_count))
					f.close()
	
	# message = await client.get_message(payload.message_id)
	# print(reaction, user)
	# await reaction.remove()

# async def on_message(self, message):
# 	print(message.content)

async def init_guild(self, guild):
	channel = discord.utils.get(guild.channels, name=submit_channel_name)
	if channel is None:
		print(f"{guild} is missing")
		return

	last_message = await channel.history().get(author__id=self.user.id)

	text = "Available options:"

	for option in options:
		text = f"{text}\n{option.get('emoji')} - {option.get('title')}"

	embed = discord.Embed()
	embed.add_field(name="Submit Ticket", value=text, inline=False)
	embed.set_footer(text="React with something!")

	if last_message is None:
		last_message = await channel.send(embed=embed)
	else:
		await last_message.edit(content="", embed=embed, supress=False)
		await last_message.clear_reactions()
	
	for option in options:
		await last_message.add_reaction(option.get('emoji'))

async def send_template(channel, mention, title, description, fields):
	embed = discord.Embed(title=title, description=description, colour=0xf1c40f)

	if not fields is None:
		for field in fields:
			embed.add_field(name=field.get("name"), value=field.get("value"), inline=field.get("inline"))

	if isinstance(mention, discord.member.Member):
		mention = mention.mention
	else:
		mention = mention

	message = await channel.send(mention, embed=embed)
	return message

async def save_transcript(channel, reason):
	output = ""
	author = None

	async for message in channel.history(limit=None):
		if len(message.mentions) > 0:
			author = message.mentions[0]

		content = message.content

		if not message.mentions is None:
			for user_mention in message.mentions:
				content = content.replace(f"<@!{user_mention.id}>", f"@{user_mention.name}#{user_mention.discriminator}")

		if content != "":
			output = f"{message.author}:\n{content}\n\n{output}"
	
	now = datetime.now()
	file_name = f"{channel.name}_{now.day}-{now.month}-{now.year}_{now.second}-{now.minute}-{now.hour}.txt"

	directory = os.getcwd()
	if is_dev:
		directory = directory + "/transcripts_dev"
	else:
		directory = directory + "/transcripts"

	if not os.path.exists(directory):
		os.mkdir(directory)
	
	path = f"{directory}/{file_name}"

	print(f"Saving transcript {file_name}...")

	with io.open(path, "w", encoding="utf-8") as f:
		f.write(output)

	transcript_channel = discord.utils.get(channel.guild.channels, name=transcript_channel_name)
	if not transcript_channel is None:
		with open(path, "rb") as fp:
			await transcript_channel.send(f"{channel.name} has been closed ({reason or 'No reason specified.'})", file=discord.File(fp, f"{channel.name}.txt"))
	
	return author

async def close(channel, reason):
	if not is_ticket(channel):
		return
	author = await save_transcript(channel, reason)
	await channel.delete()
	return author

def is_ticket(channel):
	return len(re.findall("^ticket(\-[a-zA-Z]+)?\-[0-9]+$", channel.name, flags=re.I)) > 0