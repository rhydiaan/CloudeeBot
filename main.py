from env import TOKEN, API_key
import discord
from discord.ext import commands
import requests
import asyncio

# Instantiate a discord client
client = commands.Bot(command_prefix = '~', help_command=None)


##############################################################################################################################
# 'help' command
##############################################################################################################################

async def help_embed(ctx, type): # Starts the embed to show the user how to use the functionality of the bot
    if type == "cloudee": # If the type matches "cloudee" then send the help embed for the cloudee commands
        title = "CloudeeBot"
    embed = discord.Embed( # Creating the help embed
        title=f'{title}',
        description='----------',
        colour=discord.Colour.darker_grey()
    )

    if type == "cloudee":
        embed.add_field(name='~cloudee in [Location you want current weather data from]', value='Displays an embed displaying meteorological data of specified location.', inline=False)

    await ctx.send(embed=embed) # Sending the help embed



##############################################################################################################################
# 'in' command
##############################################################################################################################

async def request_coordinates(ctx, args): # Requesting coordinates using geocode api
    place_name = '+'.join(args)
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={place_name.title()}&limit=1&appid={API_key}'
    r = requests.get(url)
    if r.status_code != 200:
        await ctx.send('Invalid place!')
    else:
        data = r.json()
        return (data[0]["lat"], data[0]["lon"]) # Returning the lon and lat in order to be used for weather api

async def request_weather(ctx, args): # Calling weather api for json file of all weather data
    lat, lon = await request_coordinates(ctx, args) # Api requires longitude and latitude so using geocode api to get those values
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric'
    r = requests.get(url)
    if r.status_code != 200:
        await ctx.send('Invalid place!')
    else:
        data = r.json()
    return data

async def main_embed(ctx, args): # Main embed to display information of the place that the user requested
    data = await request_weather(ctx, args)
    name = ' '.join(args) # Creating title of the user's requested location by joining the list of all arguments into string
    embed = discord.Embed(
            title=f'{name.title()}',
            description=f'{data["sys"]["country"]}',
            colour=discord.Colour.darker_grey()
        )
        
    embed.add_field(name='The weather:', value=f'{data["weather"][0]["description"].title()}', inline=False)
    embed.add_field(name='Temperature:', value=f'{int(data["main"]["temp"])}°C', inline=False)
    embed.add_field(name='Humidity:', value=f'{data["main"]["humidity"]}%', inline=False)
    embed.add_field(name='Wind speed:', value=f'{data["wind"]["speed"]}mph', inline=False)
    
    await ctx.send(embed=embed) # Sending embed


##############################################################################################################################
# Main command
##############################################################################################################################


@client.command()
async def cloudee(ctx, *args): # Main function command
    arguments = list(args)
    if len(arguments) in range(1,6) : # Ensuring the user is using the correct usage of the command
        if arguments[0].lower() == 'help': # Calling help embed for the user as specified by the user
            await help_embed(ctx, 'cloudee')
        elif arguments[0].lower() == 'in' and len(arguments) > 1:
            arguments.pop(0) # Popping 'in' from the arguments list to make it easier later on
            await main_embed(ctx, arguments) # Calling the main embed to display to the user
    else:
        await ctx.send('Please use ~cloudee help for more information.') # Error code if what user inputted does not work


# On ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="the skies! Use ~cloudee help for help!"))
    print('You have logged in as {0.user}'.format(client))

client.run(TOKEN)