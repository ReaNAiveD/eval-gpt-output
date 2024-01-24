import logging
import os
import time

import openai


def get_copilot(config: dict):
    def copilot(msg: str, retry=3):
        openai.api_type = "azure"
        openai.api_base = "https://clitools-copilot.openai.azure.com/"
        openai.api_version = "2023-07-01-preview"
        openai.api_key = os.getenv("API_KEY")

        messages = [{
            "role": "system",
            "content": config['systemPrompt'],
        }]
        for qa in config.get('fewShotExamples', []):
            messages.append({
                "role": "user",
                "content": qa['userInput'],
            })
            messages.append({
                "role": "assistant",
                "content": qa['chatbotResponse'],
            })
        messages.append({
            "role": "user",
            "content": msg,
        })
        chat_kwargs = {
            'engine': config['chatParameters']['deploymentName'],
            'temperature': config['chatParameters'].get('temperature', .5),
            'max_tokens': config['chatParameters'].get('maxResponseLength', 800),
            'top_p': config['chatParameters'].get('topProbablities', .95),
            'frequency_penalty': config['chatParameters'].get('frequencyPenalty', 0),
            'presence_penalty': config['chatParameters'].get('presencePenalty', 0),
            'stop': config['chatParameters'].get('stop')
        }
        while retry >= 0:
            try:
                response = openai.ChatCompletion.create(
                    messages=messages,
                    **chat_kwargs)
                content = response["choices"][0]["message"]["content"]
                return content
            except openai.OpenAIError as e:
                if retry > 0:
                    retry -= 1
                    logging.warning("Wait and Retry: " + str(e))
                    time.sleep(60)
                else:
                    raise e

    return copilot
