import discord
from time import sleep
import os
from dotenv import load_dotenv
load_dotenv()

import main

story = main.load_json("story")
location = ""

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

async def send_messages(channel, messages):
    for message in messages:
        await channel.send(message)
        sleep(1)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global location, story
    newLocation = ""

    channel = message.channel
    message = main.input_cleaner(message.content)
    
    if message == "!start":
        location = "start"
        await send_messages(channel, story[location]["messages"])
        return

    if location == "":
        await channel.send("Do !start to start the game.")
        return

    intent = main.dialogflow.detect_intent(message)

    if intent != "":
        main.debug(f"Detected intent: {intent}")

    if intent in story[location] and "messages" in story[location][intent]:
        response = story[location][intent]["messages"]
        if "location" in story[location][intent]:
            newLocation = story[location][intent]["location"]
        main.debug(f"Location has intent match")
    else:
        try:
            prompt = main.load_prompt(intent)
        except:
            prompt = main.load_prompt(story[location]["prompt"])
            main.debug(f"Falling back to location prompt {story[location]['prompt']}")

        main.debug(f"Getting response from GPT for story location {location}")

        response = main.get_response(message, story[location]["messages"], prompt)

        if "location" in prompt:
            newLocation = prompt["location"]

        if intent in story[location]:
            newLocation = story[location][intent]["location"]

    await send_messages(channel, response)

    if newLocation != "":
        location = newLocation
        main.debug(f"Location updated to {newLocation}")
        await send_messages(channel, story[location]["messages"])

client.run(os.environ.get('DISCORD_TOKEN'))
