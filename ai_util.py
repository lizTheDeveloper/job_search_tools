import json
import openai 
import os 
import time 
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
print("openai.api_key",openai.api_key)
global total_token_estimate 
total_token_estimate = 0

def clean_list(text):
    items = []
    lines = re.split('[\t\n\r][:\d)*\-.+>]+[\.\s\-)]?\s?', text)
    for line in lines:
        # strip any list notation so it is just one description per line
        bare_line = re.sub("^[:\d)*\-.+>]+", '', line.strip('- ')).strip()
        if len(bare_line) > 0:
            items.append(bare_line)
    return items


def discerning_natural_language_prompt(prompt):
    print("sending prompt:", prompt)
    global total_token_estimate

    ## estimate the number of tokens this would be by splitting on spaces
    ## and taking the length of that array
    ## this is a hacky way to do it, but it's a good enough estimate
    ## for now
    num_tokens = len(prompt.split(" "))
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1012,
            top_p=1,
            frequency_penalty=0.24,
            presence_penalty=0.23
        )
        response_text = response.get("choices", [{"text": ""}])[0].get("text","")
        total_token_estimate += num_tokens + len(response_text.split(" "))
        print("discerning_natural_language_prompt got_response ",response_text)
        print("total_token_estimate so far this run",total_token_estimate)
    except:
        ## wait 5 seconds and try again
        print("discerning_natural_language_prompt got an error, waiting 5 seconds and trying again")
        time.sleep(5)
        return discerning_natural_language_prompt(prompt)

    return response_text


def classifying_natural_language_prompt(prompt):
    print("sending prompt:", prompt)
    global total_token_estimate

    ## estimate the number of tokens this would be by splitting on spaces
    ## and taking the length of that array
    ## this is a hacky way to do it, but it's a good enough estimate
    ## for now
    num_tokens = len(prompt.split(" "))
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_text = response.get("choices", [{"text": ""}])[0].get("text","")
        total_token_estimate += num_tokens + len(response_text.split(" "))
        print("classifying_natural_language_prompt got_response ",response_text)
        print("total_token_estimate so far this run",total_token_estimate)
    except:
        ## wait 5 seconds and try again
        print("classifying_natural_language_prompt got an error, waiting 5 seconds and trying again")
        time.sleep(5)
        return classifying_natural_language_prompt(prompt)

    return response_text