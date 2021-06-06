import json
from time import sleep
import gpt3
import dialogflow
import os.path

def debug(message):
    global DEBUG
    if DEBUG:
        print("DEBUG: " + message)

def load_json(file_name):
    f = open(file_name + ".json")
    output = json.load(f)
    f.close()
    return output

def load_prompt(prompt_name):
    return load_json("prompts/" + prompt_name)

def input_cleaner(message):
    for word in ["You: ", "###", "@", "[", "]", "\\", "{", "}", "=", "%", "<", ">"]:
        if word in message:
            message = message.replace(word, "")
    return message

def format_dialogue_prompt(message, context, prompt_data):
    prompt = prompt_data["task"] + ":\n"

    for context_message in context:
        prompt += context_message + "\n"

    prompt += "\n"

    for example in prompt_data["examples"]:
        prompt += "You: " + example["input"] + "\nResponse:\n" 
        for example_output in example["output"]:
            prompt += example_output + "\n"
        prompt += "###\n"

    prompt += "You: " + message + "\nResponse:\n"
    return prompt

def format_qa_prompt(message, context, prompt_data):
    prompt = prompt_data["task"] + ":\n"

    prompt += prompt_data["context"] + "\n\n"

    for example in prompt_data["examples"]:
        prompt += "Q: " + example["input"] + "\nA:\n" 
        for example_output in example["output"]:
            prompt += example_output + "\n"
        prompt += "###\n"

    prompt += "Q: " + message + "\nA:\n"
    return prompt

def get_response(message, context, prompt_data):
    if prompt_data["type"] == "DIALOGUE":
        prompt = format_dialogue_prompt(message, context, prompt_data)
        return gpt3.response(prompt).split("Response:")[-1].replace("###", "").strip().split("\n")
    elif prompt_data["type"] == "QA":
        prompt = format_qa_prompt(message, context, prompt_data)
        return gpt3.response(prompt).split("A:")[-1].replace("###", "").strip().split("\n")
    else:
        return "ERROR: INVALID/NO PROMPT TYPE"

DEBUG = True

if __name__ == "__main__":
    story = load_json("story")
    location = "start"

    print("--- INCOMING TRANSMISSION ---")

    while True:
        for message in story[location]["messages"]:
            print(message)
            sleep(1)

        while True:
            message = input_cleaner(input("You: "))#

            newLocation = ""

            if message == "":
                continue

            # Check dialogueflow
            intent = dialogflow.detect_intent(message)

            if intent != "":
                debug(f"Detected intent: {intent}")

            if intent in story[location] and "messages" in story[location][intent]:
                response = story[location][intent]["messages"]
                if "location" in story[location][intent]:
                    newLocation = story[location][intent]["location"]
                debug(f"Location has intent match")
            else:
                try:
                    prompt = load_prompt(intent)
                except:
                    prompt = load_prompt(story[location]["prompt"])
                    debug(f"Falling back to location prompt {story[location]['prompt']}")

                debug(f"Getting response from GPT for story location {location}")

                response = get_response(message, story[location]["messages"], prompt)

                if "location" in prompt:
                    newLocation = prompt["location"]

                if intent in story[location]:
                    newLocation = story[location][intent]["location"]

            for message in response:
                print(message)
                sleep(1)

            if newLocation != "":
                location = newLocation
                debug(f"Location updated to {newLocation}")
                break

    print("End")