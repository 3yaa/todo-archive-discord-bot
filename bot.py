import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

MONITORED_CHANNEL_NAME = "todos"  
ARCHIVE_CHANNEL_NAME = "todo-archive" 

@bot.event
async def on_ready():
	print(f'bot rdy, logged in as {bot.user}')
	for guild in bot.guilds:
		await setup_channels(guild)

# find/create channels
async def setup_channels(guild):
	monitor_channel = discord.utils.get(guild.text_channels, name=MONITORED_CHANNEL_NAME)
	archive_channel = discord.utils.get(guild.text_channels, name=ARCHIVE_CHANNEL_NAME)

	# create archive channel if doesn't exist
	if archive_channel is None:
		archive_channel = await guild.create_text_channel(ARCHIVE_CHANNEL_NAME, topic="archive msgs are here", reason="AUTO MADE")

	# create monitor channel if doesn't exist
	if monitor_channel is None:
		monitor_channel = await guild.create_text_channel(MONITORED_CHANNEL_NAME, topic="monitoring channel", reason="AUTO MADE")
	
@bot.event
async def on_message_delete(msg):
	if msg.channel.name != MONITORED_CHANNEL_NAME:
		return
	
	if msg.author.bot:
		return
	
	archive_channel = discord.utils.get(msg.guild.text_channels, name=ARCHIVE_CHANNEL_NAME)

	# msg header
	header = f"**Task Completed** by {msg.author.mention} at <t:{int(msg.created_at.timestamp())}:f>\n"
	separator = "─" * 13
	
	# task
	await archive_channel.send(
		f"{header}{separator}\n{msg.content}\n"
	)
	
	# attachment separate
	if msg.attachments:
		for att in msg.attachments:
			await archive_channel.send(att.url)

@bot.command()
@commands.has_permissions(administrator=True)
async def monitor(ctx, channel_name: str):
	global MONITORED_CHANNEL_NAME
	MONITORED_CHANNEL_NAME = channel_name
	await ctx.send(f"NOW MONITORING #{channel_name}")

bot_token = os.getenv("TOKEN")
if bot_token is None:
    print("ERROR: bot_token not found")
else:
    bot.run(bot_token)