import discord
import random
from config import TOKEN, SERVERS, HOH_ROLE_ID
from classes import Bot, BotEmbed, SetConfView, UnlinkConfView
from database import *

bot = Bot()

#################### BASICS ####################

@bot.event
async def on_ready() -> None:
	print("\nJulie Chen connected and ready to Rock n' Roll !\n")

@bot.slash_command(guild_ids=SERVERS, name="ping", description="PONG !")
async def ping(interaction: discord.Interaction) -> None:
	print(f"COMMAND : /ping used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	await interaction.response.send_message(embed=BotEmbed(title="PONG !", colour=discord.Colour.green()).remove_footer(), ephemeral=True)

##################### CORE #####################

@bot.slash_command(guild_ids=SERVERS, name="crownhoh", description="Select the Head of Household winner.")
async def crownhoh(interaction: discord.Interaction, user: discord.Member = discord.Option(discord.Member, description="The member who won the Head of Household", required=True)) -> None:
	print(f"COMMAND : /crownhoh used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	colour: discord.Colour = discord.Colour.from_rgb(get_r(1), get_g(1), get_b(1))
	embed = BotEmbed(title="Head Of Household Winner <:HOH:1267582814082302004>", description=f"{user.mention} Has Won Head Of Household!", colour=colour)
	gifs: list[str] = ["https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXo0a2NjbXRrb3lyNHk2dzMzY2kzeDIyN3gxaWN0am02M2ZnOW9oZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/05No0Hw1hWyAEPNWDA/giphy.gif",
					"https://media1.tenor.com/images/e5c7b812d290ec41846b17532eb812e7/tenor.gif?itemid=5308822",
					"https://media2.giphy.com/media/JGwttvfIFHD0ZZVJrp/giphy.gif?cid=790b7611b357d48a6003113fffa9d39adcd7ed148d17296a&rid=giphy.gif&ct=g",
					"https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXZiNG8zbWQ5bGg0c25kbnhrN2kzeG1zNXppeXhzYTMzNGt3ejMyZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/bn7ejXVhQo0RaTzFXP/giphy.gif",
					"https://i.imgur.com/mGYTz.gif"]
	chosen_gif: str = gifs[random.randint(0, 4)]
	embed.image = chosen_gif
	hoh_role: discord.Role = interaction.guild.get_role(HOH_ROLE_ID)
	await user.add_roles(hoh_role, reason="Won the HoH")
	await interaction.response.send_message(embed=embed)

@bot.slash_command(guild_ids=SERVERS, name="vetowinner", description="Select the Power of Veto winner.")
async def vetowinner(interaction: discord.Interaction, user: discord.Member = discord.Option(discord.Member, description="The member who won the Power of Veto", required=True)) -> None:
	print(f"COMMAND : /vetowinner used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	...

################### DATABASE ###################

@bot.slash_command(guild_ids=SERVERS, name="set_confessional", description="Set a Text Channel as a confessional for the given user")
async def set_confessional(interaction: discord.Interaction,
						   user: discord.Member = discord.Option(discord.Member, description="The user to link to a confessional", required=True),
						   channel_id: discord.TextChannel = discord.Option(str, description="The ID of the confessional of the user", required=True)) -> None:
	print(f"COMMAND : /set_confessional used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	if (is_user_in_database(user)):
		if (get_confessional(user) == int(channel_id)):
			await interaction.response.send_message(embed=BotEmbed(title="CONFESSIONAL ALREADY SET", description=f"{user.mention} is already linked to #{interaction.guild.get_channel(int(channel_id)).name}."))
		else:
			embed = BotEmbed(title="CONFESSIONAL ALREADY SET", description=f"A confessional is already stored in the database for {user.mention} (#{interaction.guild.get_channel(get_confessional(user)).name})")
			embed.add_field(name="Do you want to change it ?", value=" ✅ Do nothing.\n ♻️ Modify with the new channel.", inline=False)
			view: discord.ui.View = SetConfView(user, channel_id)
			await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
	else:
		add_confessional(user, channel_id)
		await interaction.response.send_message(embed=BotEmbed(title="CONFESSIONAL ADDED", description=f"New confessional linked for {user.mention} (#{interaction.guild.get_channel(int(channel_id)).name}).", colour=discord.Colour.green()), ephemeral=True)

@bot.slash_command(guild_ids=SERVERS, name="unlink_confessional", description="Unlink the user to the confessional associated")
async def unlink_confessional(interaction: discord.Interaction,
							  user: discord.Member = discord.Option(discord.Member, description="The user to remove from the database", required=True)) -> None:
	print(f"COMMAND : /unlink_confessional used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	if (not is_user_in_database(user)):
		await interaction.response.send_message(embed=BotEmbed(title="NO CONFESSIONAL LINKED", description=f"No confessional found in the database for {user.mention}."))
	else:
		embed = BotEmbed(title="UNLINK CONFESSIONAL ?", description=f"Do you really want to unlink {user.mention}'s confessional ?\nIf you just want to modify the confessional's channel, you can just use **/set_confessional** with the ID of the new confessional.")
		view = UnlinkConfView(user)
		await interaction.response.send_message(embed=embed, view=view)

@bot.slash_command(guild_ids=SERVERS, name="display_confessionals", description="Show the list of the users linked to a confessional")
async def display_confessionals(interaction: discord.Interaction) -> None:
	print(f"COMMAND : /display_confessionals used by @{interaction.user.name} in {interaction.guild.name} (#{interaction.channel.name})")
	nb_confessionals: int = get_nb_confessionals()
	if (nb_confessionals == 0):
		return await interaction.response.send_message(embed=BotEmbed(title="CONFESSIONALS LIST", description=f"No players linked to confessionals for now."))
	elif (nb_confessionals == 1):
		embed = BotEmbed(title="CONFESSIONALS LIST", description=f"**{nb_confessionals}** player linked to confessionals :")
	else:
		embed = BotEmbed(title="CONFESSIONALS LIST", description=f"**{nb_confessionals}** players linked to confessionals :")
	confessionals: list = get_confessionals_list()
	for element in confessionals:
		embed.add_field(name=f"", value=f"{interaction.guild.get_member(int(element[0])).mention}	---	{interaction.guild.get_channel(int(element[1])).mention}", inline=False)
	return await interaction.response.send_message(embed=embed)

#################### CONFIG ####################

@bot.slash_command(guild_ids=SERVERS, name="set_hoh_rgb", description="Set the color of the Head of Household embed")
async def set_hoh_rgb(interaction: discord.Interaction,
					  red: int = discord.Option(int, description="Red (0-255)", min_value=0, max_value=255, required=True),
					  green: int = discord.Option(int, description="Green (0-255)", min_value=0, max_value=255, required=True),
					  blue: int = discord.Option(int, description="Blue (0-255)", min_value=0, max_value=255, required=True)) -> None:
	if (not (red >= 0 and red <= 255)):
		embed = BotEmbed(title="ERROR", description="Red value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	elif (not (green >= 0 and green <= 255)):
		embed = BotEmbed(title="ERROR", description="Green value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	elif (not (blue >= 0 and blue <= 255)):
		embed = BotEmbed(title="ERROR", description="Blue value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		set_embed_rgb(1, red, green, blue)
		colour: discord.Colour = discord.Colour.from_rgb(get_r(1), get_g(1), get_b(1))
		embed = BotEmbed(title="COLOR MODIFIED", description=f"The color of the **Head of Household** embed had been successfuly modified to r={red}, g={green}, b={blue}", colour=colour)
		return await interaction.response.send_message(embed=embed)

@bot.slash_command(guild_ids=SERVERS, name="set_veto_rgb", description="Set the color of the Power of Veto embed")
async def set_veto_rgb(interaction: discord.Interaction,
					  red: int = discord.Option(int, description="Red (0-255)", min_value=0, max_value=255, required=True),
					  green: int = discord.Option(int, description="Green (0-255)", min_value=0, max_value=255, required=True),
					  blue: int = discord.Option(int, description="Blue (0-255)", min_value=0, max_value=255, required=True)) -> None:
	if (not (red >= 0 and red <= 255)):
		embed = BotEmbed(title="ERROR", description="Red value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	elif (not (green >= 0 and green <= 255)):
		embed = BotEmbed(title="ERROR", description="Green value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	elif (not (blue >= 0 and blue <= 255)):
		embed = BotEmbed(title="ERROR", description="Blue value must be between 0 and 255.", colour=discord.Colour.red())
		return await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		set_embed_rgb(2, red, green, blue)
		colour: discord.Colour = discord.Colour.from_rgb(get_r(2), get_g(2), get_b(2))
		embed = BotEmbed(title="COLOR MODIFIED", description=f"The color of the **Power of Veto** embed had been successfuly modified to r={red}, g={green}, b={blue}", colour=colour)
		return await interaction.response.send_message(embed=embed)

bot.run(TOKEN)