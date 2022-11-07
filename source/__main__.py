# Imported Modules
import asyncio
import discord
import inspect
import mariadb
import os
import pkgutil
import re
import string
import sys
import threading
import traceback

intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Color Modules
from colorama import init
from termcolor import colored

init(autoreset=True)

# Custom Modules
import commands
import secrets
import tickets
import utils

# Initialization
prefix = ';'

# Load Modules
__all__ = dir()

modules = []

for module_name in __all__:
	try:
		module = globals()[module_name]
		if inspect.ismodule(module):
			modules.append(module)
			for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__):
				if not is_pkg and module_name != __name__:
					try:
						name = re.sub("^.+\.", "", module_name)
						_module = loader.find_module(module_name).load_module(module_name)
						if _module != module:
							modules.append(_module)
					except:
						pass
	except:
		continue

print(colored(f"Loaded {len(modules)} modules!", "cyan"))

# Load Commands
command_modules = {}

for loader, module_name, is_pkg in pkgutil.walk_packages(commands.__path__):
	if not is_pkg:
		try:
			name = re.sub("^.+\.", "", module_name)
			module = loader.find_module(module_name).load_module(module_name)
			command_modules[name] = module
			print(colored(f"Loaded command: {module_name}", "yellow"))
		except:
			pass

def set_interval(func, sec, guild):
	def func_wrapper():
		set_interval(func, sec, guild)
		func(guild)
	t = threading.Timer(sec, func_wrapper)
	t.start()
	return t

def update(guild):
	print(guild.members)

async def invoke(function_name, *argv):
	for module in modules:
		try:
			if hasattr(module, function_name):
				await getattr(module, function_name)(*argv)
		except:
			traceback.print_exc()
			continue

async def invoke_command(command, target, self, message):
	try:
		module = command_modules.get(command)
		await getattr(module, target)(self, message)
		return True
	except AttributeError as e:
		return False
	except:
		traceback.print_exc()
		await warn_op(message.channel)
		return False

async def warn_op(channel):
	await channel.send("Error detected, restarting bot!")
	quit()

# Discord client
class NonstopClient(discord.Client):
	async def on_ready(self):
		print(colored(f"User ready: {self.user}", "green"))
		
		for guild in self.guilds:
			print(colored(f"Initializing {guild}...", "green"))
			await invoke("on_ready", self, guild)
			# set_interval(update, 1.0, guild)

	async def on_guild_channel_create(*kargs):
		await invoke("on_guild_channel_create", *kargs)

	async def on_guild_channel_delete(*kargs):
		await invoke("on_guild_channel_delete", *kargs)

	async def on_guild_channel_update(*kargs):
		await invoke("on_guild_channel_update", *kargs)

	async def on_raw_message_delete(*kargs):
		await invoke("on_raw_message_delete", *kargs)

	async def on_raw_bulk_message_delete(*kargs):
		await invoke("on_raw_bulk_message_delete", *kargs)

	async def on_raw_message_edit(*kargs):
		await invoke("on_raw_message_edit", *kargs)

	async def on_raw_reaction_add(*kargs):
		await invoke("on_raw_reaction_add", *kargs)

	async def on_raw_reaction_remove(*kargs):
		await invoke("on_raw_reaction_remove", *kargs)
		
	async def on_raw_reaction_clear(*kargs):
		await invoke("on_raw_reaction_clear", *kargs)

	async def on_member_join(*kargs):
		await invoke("on_member_join", *kargs)

	async def on_member_remove(*kargs):
		await invoke("on_member_remove", *kargs)
	
	async def on_member_update(*kargs):
		await invoke("on_member_update", *kargs)

	async def on_message(self, message):
		if message.guild is None:
			# print(f"{message.author} -> {self.user}: {message.content}")
			return

		await invoke("on_message", self, message)
		
		channel = message.channel

		if not hasattr(message.author, "roles") or message.author.roles is None:
			return
		
		try:
			if type(message.mentions) is list and len(message.mentions) > 0 and message.mentions[0] == self.user:
				await channel.send("What do you want!?")

			isAdmin = discord.utils.get(message.author.roles, name="Support Team") is not None or discord.utils.get(message.author.roles, name="Staff Team") is not None or discord.utils.get(message.author.roles, name="Senior Staff Team") is not None or discord.utils.get(message.author.roles, name="Management") is not None

			if message.content[0:1] != prefix:
				return
			
			content = re.sub("^\s", "", re.sub("\ +", " ", message.content)) # Deprec
			args = content[1:len(content)].split(" ") # Deprec
			command = args[0].lower()

			# Invoke commands
			await invoke_command(command, "on_command", self, message)

			# Invoke admin commands
			if isAdmin:
				await invoke_command(command, "on_admin_command", self, message)
			else:
				return
			
			# Channels
			logChannel = discord.utils.get(message.guild.text_channels, name="warning-logs")
			publicLogChannel = discord.utils.get(message.guild.text_channels, name="public-warning-logs")

			# Whitelisting
			# elif command == "unwhitelist":
			# 	if len(args) < 3:
			# 		await channel.send("{0}, the format is: unwhitelist <user/hex>".format(message.author.mention))
			# 		return
				
			# 	selects = "id, steam, discord"

			# 	if not await utils.db.get_target(message.mentions, args[1], message, selects):
			# 		return

			# 	# Get the result
			# 	for (id, steam, user,) in utils.db.cur:
			# 		role = discord.utils.get(message.guild.roles, name="Whitelisted")

			# 		# Find if they exist
			# 		utils.db.cur.execute("UPDATE users SET priority=-128 WHERE steam=%s", (steam,))

			# 		await message.delete()
			# 		await channel.send(f"<@{user}> ({id}) has been unwhitelisted as {steam}...")

			# 		return
			if command == "warnings":
				if len(args) < 2:
					await channel.send("{0}, the format is: warnings <user/hex> - gets the warnings from somebody".format(message.author.mention))
					return
				
				selects = "id, steam, discord, name"

				if not await utils.db.get_target(message.mentions, args[1], message, selects):
					return

				# Get the result
				for (id, steam, user, name,) in utils.db.cur:
					embed = discord.Embed(title=f"{name}'s Warnings")
					utils.db.cur.execute("SELECT id, points, info, DATE_FORMAT(time_stamp + INTERVAL 5 HOUR, '%H:%i %m/%e/%y UTC'), TIMESTAMPDIFF(DAY, CURRENT_TIMESTAMP(), time_stamp) AS 'expired' FROM `warnings` WHERE user_id=?", (id,))

					totalPoints = 0
					recentPoints = 0
					lessRecentPoints = 0

					# Get the result
					for (_id, points, info, time_stamp, expired,) in utils.db.cur:
						if expired > -60:
							lessRecentPoints += points
						if expired > -30:
							recentPoints += points
						totalPoints += points
						embed.add_field(name=f"{points} points - {time_stamp} - ID: {_id}", value=info, inline=False)

					embed.description = f"{lessRecentPoints} points within 60 days\n{recentPoints} points within 30 days\n{totalPoints} total points"

					await channel.send(f"<@!{user}> (Steam: {steam})", embed=embed)

					return
			elif command == "warningadd":
				if len(args) < 4:
					await channel.send("{0}, the format is: warningadd <user/hex> <points> <info> - add a warning".format(message.author.mention))
					return
				
				selects = "id, steam, discord, name"
				if not await utils.db.get_target(message.mentions, args[1], message, selects):
					return

				points = args[2]

				try:
					points = int(points)
				except:
					await channel.send(f"{message.author.mention}, points must be a number!")
					return

				args.pop(2)
				args.pop(1)
				args.pop(0)

				info = (' ').join(args)

				if len(info) > 2048:
					await channel.send(f"{message.author.mention}, the report must be 2048 characters or less!")
					return

				# Get the result
				for (id, steam, user, name,) in utils.db.cur:
					utils.db.cur.execute("INSERT INTO `warnings` SET user_id=?, points=?, info=?", (id, points, info,))
					utils.db.conn.commit()

					utils.db.cur.execute("SELECT LAST_INSERT_ID()")

					insert_id = utils.db.cur.fetchone()[0]
					
					await channel.send(f"<@!{user}> ({steam}) has been warned (id: {insert_id})!")

					embed = discord.Embed(title="Warning Added", description=info)
					embed.add_field(name="ID", value=f"{insert_id}", inline=False)
					embed.add_field(name="Warned By", value=f"{message.author.name}#{message.author.discriminator}", inline=False)
					embed.add_field(name="Target", value=f"Name: {name}\nID: {id}\nSteam: {steam}", inline=False)
					embed.add_field(name="Warning Points", value=points, inline=False)

					await logChannel.send(embed=embed)

					if points > 0:
						embed = discord.Embed(title="Warning Added", description=info, colour=discord.Colour.red())

						await publicLogChannel.send(embed=embed)

					return
			elif command == "warningrem":
				if len(args) < 2:
					await channel.send("{0}, the format is: warningrem <id> - remove a warning by id".format(message.author.mention))
					return
				
				utils.db.cur.execute("SELECT id, user_id, (SELECT steam FROM users WHERE user_id=id), DATE_FORMAT(time_stamp + INTERVAL 5 HOUR, '%H:%i %m/%e/%y UTC'), points, info FROM `warnings` WHERE id=?", (args[1],))

				# Get the result
				for (id, user_id, steam, time_stamp, points, info,) in utils.db.cur:
					utils.db.cur.execute("DELETE FROM `warnings` WHERE id=?", (id,))
					utils.db.conn.commit()
					
					await channel.send(f"{message.author.mention} removed warning {id}!")

					if points > 0:
						embed = discord.Embed(title="Warning Removed")
						embed.add_field(name="Removed By", value=f"{message.author.name}#{message.author.discriminator}", inline=False)
						embed.add_field(name="User", value=f"ID: {user_id}\nSteam: {steam}", inline=False)
						embed.add_field(name="Time Stamp", value=time_stamp, inline=False)
						embed.add_field(name="Warning Points", value=points, inline=False)
						embed.add_field(name="Info", value=info, inline=False)

						await logChannel.send(embed=embed)

					return
				await channel.send(f"{message.author.mention}, that warning couldn't be found!")
			elif command == "warningedit":
				# if len(args) < 4:
				# 	await channel.send("{0}, the format is: warningedit <id> <points> <info> - edit a warning".format(message.author.mention))
				# 	return
				
				# selects = "id, steam, discord, name"
				# if not await utils.db.get_target(message.mentions, args[1], message, selects):
				return

				# points = args[2]

				# args.pop(2)
				# args.pop(1)
				# args.pop(0)

				# info = (' ').join(args)

				# # Get the result
				# for (id, steam, user, name,) in utils.db.cur:
				# 	utils.db.cur.execute("INSERT INTO `warnings` SET user_id=?, points=?, info=?", (id, points, info,))
				# 	utils.db.conn.commit()
					
				# 	await channel.send(f"<@!{user}> ({steam}) has been warned!")

				# 	return
				return
			elif command == "updatechannels":
				category = discord.utils.get(message.guild.categories, name="Businesses")
				announcements = discord.utils.get(message.guild.text_channels, name="business-announcements", category=category)
				
				if category is None:
					return
				
				utils.db.cur.execute("SELECT `name`, (SELECT `discord` FROM `users` WHERE `id`=(SELECT `user_id` FROM `characters` WHERE `id`=`character_id`)) FROM businesses")

				# Get the result
				for (name, user,) in utils.db.cur:
					owner = discord.utils.get(message.guild.members, id=int(user[len("discord:"):len(user)]))
					if owner is None:
						await channel.send(f"Couldn't find user '{user}' for business '{name}'")
						return
					
					# await channel.send(f"{owner.mention}")
					channelName = re.sub('\-+', '-', re.sub("[^0-9a-zA-Z\-]+", "", re.sub("\s", "-", name.lower())))
					businessChannel = discord.utils.get(message.guild.text_channels, name=channelName)
					if businessChannel is None:
						businessChannel = await message.guild.create_text_channel(channelName, category=category)
						await channel.send(f"Made channel <#{businessChannel.id}>")

					overwrites = businessChannel.overwrites_for(owner)
					if overwrites.is_empty():
						await businessChannel.send(f"Congratulations, {owner.mention}! You now own a business.")

					overwrite = discord.PermissionOverwrite()
					overwrite.attach_files = True
					overwrite.embed_links = True
					overwrite.mention_everyone = True
					overwrite.read_message_history = True
					overwrite.read_messages = True
					overwrite.send_messages = True

					await businessChannel.set_permissions(owner, overwrite=overwrite)

					overwrite = discord.PermissionOverwrite()
					overwrite.read_message_history = True
					overwrite.read_messages = True

					await announcements.set_permissions(owner, overwrite=overwrite)
				return
			elif command == "testticket":
				if len(re.findall("ticket\-", channel.name, flags=re.I)) == 0:
					await channel.send("You should do that in a ticket. :)")
					return
				
				await tickets.init_channel(channel)
			elif command == "echo":
				if type(message.channel_mentions) is not list or message.channel_mentions == 0:
					return
				
				target = message.channel_mentions[0]

				args.pop(1)
				args.pop(0)

				text = (' ').join(args)

				await message.delete()
				await target.send(text)
		except:
			traceback.print_exc()
			await warn_op(message.channel)

client = NonstopClient(intents=intents)

if "enable_dev" in sys.argv:
	client.run(secrets.token_dev)
else:
	client.run(secrets.token)