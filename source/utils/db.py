import discord
import mariadb
import secrets

try:
	conn = mariadb.connect(
		user = secrets.conn_user,
		password = secrets.conn_password,
		host = secrets.conn_host,
		port = secrets.conn_port,
		database = secrets.conn_database
	)
	dev_conn = mariadb.connect(
		user = secrets.dev_conn_user,
		password = secrets.dev_conn_password,
		host = secrets.dev_conn_host,
		port = secrets.dev_conn_port,
		database = secrets.dev_conn_database
	)
except mariadb.Error as e:
	print(f"Error connecting to MariaDB Platform: {e}")
	sys.exit(1)

cur = conn.cursor()
dev_cur = dev_conn.cursor()

async def get_target(target, target_string, message, selects):
	isUser = False
	
	# Get user
	if type(target) is list:
		if len(target) == 0:
			if type(target_string) is str:
				target = target_string
				if target.startswith("steam:"):
					target = target[6:len(target)]
			else:
				target = None
		else:
			target = target[0]
	
	# Check name
	if target is None:
		return False
	elif type(target) is discord.member.Member:
		isUser = True

	if isUser:
		cur.execute("SELECT " + selects + " FROM users WHERE discord=%s", (target.id,))
	else:
		cur.execute("SELECT " + selects + " FROM users WHERE steam=%s", (target,))

	return True

async def dev_get_target(target, target_string, message, selects):
	isUser = False
	
	# Get user
	if type(target) is list:
		if len(target) == 0:
			if type(target_string) is str:
				target = target_string
				if target.startswith("steam:"):
					target = target[6:len(target)]
			else:
				target = None
		else:
			target = target[0]
	
	# Check name
	if target is None:
		return False
	elif type(target) is discord.member.Member:
		isUser = True

	if isUser:
		dev_cur.execute("SELECT " + selects + " FROM users WHERE discord=%s", (target.id,))
	else:
		dev_cur.execute("SELECT " + selects + " FROM users WHERE identifier=%s", (target,))

	return True