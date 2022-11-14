import discord
import re

from datetime import datetime
from datetime import timedelta

shoutouts = {}

async def update_streamer_role(self, user, guild):
	if user.activities is None:
		print(user.activities)
	
	activity_type = None
	try:
		activity_type = user.activity.type
	except:
		pass

	stream_activity = None
	role = discord.utils.get(guild.roles, name="Streamer")
	if role is None:
		print("Missing streamer role!")
		return

	if not user.activities is None:
		stream_activity = discord.utils.get(user.activities, type=discord.ActivityType.streaming)

	if stream_activity is None or len(re.findall("non\s*stop\s*r(?:ole)?\s*p(?:lay)?", stream_activity.name, flags=re.I)) <= 0:
		if role in user.roles:
			await user.remove_roles(role, reason="Stoped streaming")
	elif role not in user.roles:
		await user.add_roles(role, reason="Started streaming")
		streamsChannel = discord.utils.get(guild.channels, name="🎥│live-streams")
		now = datetime.now()
		if not streamsChannel is None and (shoutouts.get(user.id) is None or now > shoutouts.get(user.id) + timedelta(hours=6)):
			shoutouts[user.id] = now
			await streamsChannel.send(f"{user.mention} is live!\n{stream_activity.url}")

async def on_member_update(self, before, after):
	for guild in self.guilds:
		if guild.get_member(after.id):
			await update_streamer_role(self, after, guild)