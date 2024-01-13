from custom_detail_logger import CustomDetailLogger
from dataclasses import dataclass, field
import datetime
import logging
from openai import AsyncOpenAI, BadRequestError
import textwrap
import time
from typing import List, Optional
from yaml_dumper import YamlDumper

@dataclass
class ChatGptRequestParameters:
    frequency_penalty: float = 0.0
#    max_tokens: int = -1
    messages: list = field(default_factory=list)  # Avoid mutable default arguments
    model: str = None
    presence_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0

    @property
    def system_messages(self) -> List[str]:
        return [message['content'] for message in self.messages if message['role'] == 'system']

    @system_messages.setter
    def system_messages(self, new_system_messages: List[str]):
        # Remove all existing system messages
        self.messages = [message for message in self.messages if message['role'] != 'system']
        # Add new system messages
        self.messages.extend([{"role": "system", "content": msg} for msg in new_system_messages])

    @property
    def user_messages(self) -> List[str]:
        return [message['content'] for message in self.messages if message['role'] == 'user']

    @user_messages.setter
    def user_messages(self, new_user_messages: List[str]):
        # Remove all existing system messages
        self.messages = [message for message in self.messages if message['role'] != 'user']
        # Add new system messages
        self.messages.extend([{"role": "user", "content": msg} for msg in new_user_messages])


class ChatGptAsyncClient:
    def __init__(self, api_key: str, api_url: Optional[str] = None):
        self.api_key = api_key
        self.api_url = api_url
        logger = logging.getLogger(__name__)
        logger.debug("openai key: %s", api_key)
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def make_request(self, request: ChatGptRequestParameters) -> str:
        logger = logging.getLogger(__name__)
        if logger.isEnabledFor(logging.DEBUG) and logger.detail_level >= 3:
            with open("openai_requests.yaml","a") as of:
                of.write(datetime.datetime.now().strftime("# %Y-%m-%d %H:%M:%S - REQUEST: #\n"))
                of.write(YamlDumper.to_yaml_compatible_str(request))
                of.write("\n")
        if request.messages == None or len(request.messages) == 0:
            logger.error("request.messages is null or empty:\n" + YamlDumper.to_yaml_compatible_str(request))
            raise ValueError("request.messages is null or empty")
        if request.system_messages == None or len(request.system_messages) == 0:
            logger.error("request.system_messages is null or empty:\n" + YamlDumper.to_yaml_compatible_str(request))
            raise ValueError("request.system_messages is null or empty")
        logger.debug("* Calling openai *")
        try_again = True
        tries = 0
        while try_again:
            try_again = False
            tries = tries + 1
            try:
                response = await self.client.chat.completions.create(
                    messages = request.messages,
                    model = request.model
                )
            except BadRequestError as e:
                logger.error("Bad request error\n" + YamlDumper.to_yaml_compatible_str(e))
                logger.error("request:\n" + YamlDumper.to_yaml_compatible_str(request))
                if request.system_messages != None \
                    and len(request.system_messages) > 0 \
                    and request.user_messages != None \
                    and len(request.user_messages) > 0:
                    if tries < 3:
                        logger.error("Trying again")
                        try_again = True
                        time.sleep(1)
                    else:
                        logger.error("Giving up")
                        raise e
                    try_again = True

        if logger.isEnabledFor(logging.DEBUG) and logger.detail_level >= 3:
            with open("openai_requests.yaml","a") as of:
                of.write(datetime.datetime.now().strftime("# %Y-%m-%d %H:%M:%S - RESPONSE: #\n"))
                # of.write(YamlDumper.to_yaml_compatible_str(response.choices[0].message.content))
                of.write(response.choices[0].message.content)
                of.write("\n")
        return response
    


