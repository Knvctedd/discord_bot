import discord
import datetime

async def on_admin_command(self, message):
	change_text = format_changelog(message.content[len("changelog") + 2:len(message.content)])

	channel = discord.utils.get(message.guild.text_channels, name="change-log")
	embed = discord.Embed(title=get_timestamp(), description=change_text, colour=discord.Colour.blue())
	
	msg = await channel.send(embed=embed)
	await msg.publish()

def get_timestamp():
	date = datetime.datetime.now()
	day_of_month = date.day
	week_number = (day_of_month - 1) // 7 + 1
	datetime_object = datetime.datetime.strptime(str(date.month), "%m")
	month_name = datetime_object.strftime("%B")
	
	return f"{month_name} {date.year} - Week {str(week_number)}"

def format_changelog(text):
	formatted = ""
	lines = text.splitlines()
	newLines = []
	last_user = "?"

	for line in lines:
		if line[0:1] == "#":
			last_user = line[2:len(line)]
		elif line != "":
			newLines.append("- " + line + " *(" + last_user + ")*")
	
	newLines.sort()

	for line in newLines:
		if formatted != "":
			formatted = formatted + "\n"
		formatted = formatted + line

	return formatted