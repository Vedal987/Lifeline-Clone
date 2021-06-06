#import openai
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
#openai.api_key = os.environ.get('OPENAI_API_KEY')
API_TOKEN = os.environ.get('HUGGINGFACE_API_KEY')

def query(prompt, parameters=None, options={'use_cache': False}):

    """
    openai.Completion.create(engine='davinci',
                                prompt=prompt,
                                max_tokens=48,
                                temperature=0.9,
                                top_p=1,
                                n=1,
                                frequency_penalty=0.4,
                                presence_penalty=0.6,
                                stream=False,
                                stop="\n")["choices"][0]["text"].strip()
    """

    API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    body = {"inputs":prompt,'parameters':parameters,'options':options}
    response = requests.request("POST", API_URL, headers=headers, data= json.dumps(body))
    try:
      response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Prompt:")
        print(prompt)
        return "API Error: "+" ".join(response.json()['error'])
    else:
      return response.json()[0]['generated_text']

def response(prompt):
    parameters = {
        'max_new_tokens': 100,  # number of generated tokens
        'temperature': 0.3,   # controlling the randomness of generations
        'end_sequence': "###" # stopping sequence for generation
    }
    response = query(prompt, parameters)
    return response