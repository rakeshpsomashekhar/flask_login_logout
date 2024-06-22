import requests

#defaults
defaultURL = 'https://langserve-launch-example-vz4y4ooboq-uc.a.run.app/'
defaultTemperature = 'medium_temp'
defaultPrompt = 'You are an AI helpful assistant'

class HolcimCopilotBackend:
    def __init__(self, prompt: str = defaultPrompt, temperature: str = defaultTemperature):
        self.prompt = prompt
        self.temperature = temperature

    def callLLM(self, userQuestion: str):
        response = requests.post(
            defaultURL + "invoke",
            json={ 'input': {'topic': 'You are an AI helpful assistant'},
                'config': {'configurable': 
                                {
                                'llm': self.temperature,
                                'prompt': userQuestion
                                }
                            },
                    'kwargs': {}
                }
        )
        answer = response.json()
        print(answer)
        return answer

holcimCopilotBackend = HolcimCopilotBackend()
