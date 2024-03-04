import ast
import json
import requests
import warnings
from abc import ABC
from typing import Dict, List
from pydantic import BaseModel
from fastprogress.fastprogress import master_bar, progress_bar
from .._utils.llm_utils import completion_message
from .._utils.llm_utils import SYSTEM_PROMPT, TASK_EXAMPLE, MAPPING_DICT
from ._prompt_schema import textclassifierprompt, nerprompt

HAS_TENACITY = True
try:
    import tenacity
except:
    HAS_TENACITY = False


if HAS_TENACITY:
    from tenacity import stop_after_attempt, wait_exponential, retry_if_exception_type


def retry(func):
    if HAS_TENACITY:
        return tenacity.retry(
            stop=stop_after_attempt(5),
            wait=wait_exponential(min=5, max=60),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )(func)
    return func


@retry
def calling_api(url, header, payload):
    s = requests.request(
        method="POST", url=url, headers=header, data=json.dumps(payload)
    )
    if s.status_code == 404:
        raise requests.exceptions.ConnectionError(
            f"Please verify the LLM configuration. Provided {s.json()['error']['message']}"
        )
    elif s.status_code == 429:
        # raise requests.exceptions.TooManyRedirects(f"{s.json()['error']['message']}")
        raise requests.exceptions.TooManyRedirects(
            f"The API has exceeded the allocated rate limit."
        )
    elif s.status_code == 401:
        raise Exception(
            f"The API key appears to be invalid. Please verify the LLM parameters."
        )
    elif s.status_code >= 400:
        # raise Exception(f"{s.json()['error']['message']}")
        print(f"{s.json()['error']['message']}")
        raise Exception(
            "The API server has encountered an error. Please try again later."
        )
    return s


class AbstractLLM(ABC):
    def __init__(self, **llm_config) -> None:
        if llm_config is None:
            llm_config = {}
        self.API_BASE = llm_config.get("api_base_or_org_name", None)

        self.API_KEY = llm_config.get("api_key", None)

        self.API_VERSION = llm_config.get("api_version", "2023-05-15")
        self.API_TYPE = llm_config.get("api_type", None)
        self.model_name = llm_config.get("api_model", "gpt-35-turbo-16k")
        self.engine = llm_config.get("api_engine", None)
        self.temperature = llm_config.get("temperature", 0.1)
        self.agent = llm_config.get("agent", None)

        if self.API_TYPE == "azure":
            assert (
                self.API_KEY is not None and self.API_BASE is not None
            ), "LLM config must be supplied."
        elif self.API_TYPE == "openai":
            assert (
                self.API_KEY is not None
            ), "LLM config must have following keys - `api_key` and `api_type`"
        else:
            raise Exception(f"llm_params should include `api_type` set to `openai`")
        self.header = None


# wrap the llm base class
class llm_base(AbstractLLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_agent()
        self.max_token = 4096

    def setup_agent(self):
        if self.API_TYPE == "azure":
            self.header = {"Content-Type": "application/json", "api-key": self.API_KEY}
            self.API_BASE = f"{self.API_BASE}/openai/deployments/{self.engine}/chat/completions?api-version={self.API_VERSION}"
        else:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_KEY}",
            }
            self.API_BASE = f"https://api.openai.com/v1/chat/completions"

    def _validate_prompt_length(self, message):
        return True

    def __call__(self, *args, **kwargs):
        """
        This module will make the LLM calls internally
        :param args:
        :param kwargs:
        :return:
        """
        system_message = kwargs.get("system", None)
        messages = kwargs.get("messages", None)
        show_progress = kwargs.get("show_progress", False)
        if isinstance(messages, str):
            messages = [messages]

        payload = []

        for message in messages:
            if self._validate_prompt_length(f"{system_message}\n\n{message}"):
                payload.append(
                    {
                        "messages": [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": f"{message}"},
                        ],
                        "temperature": 0.2,
                    }
                )

        if not HAS_TENACITY:
            raise Exception("tenacity package is missing from envi")

        final_resp = []
        if len(payload):
            for data in progress_bar(payload, display=show_progress):
                try:
                    if self.API_TYPE == "openai":
                        data["model"] = "gpt-3.5-turbo-16k"
                    s = calling_api(self.API_BASE, self.header, data)
                except requests.exceptions.ConnectionError as e:
                    return str(e), 1
                except requests.exceptions.TooManyRedirects as e:
                    return str(e), 1
                except Exception as e:
                    return str(e), 1

                if s.status_code == 200:
                    final_resp.append(completion_message(s.json()).generations)
                else:
                    final_resp.append(completion_message([]).generations)
        return final_resp, 0


class caller:
    def __init__(self, **kwargs):
        self.token = kwargs.get("token", None)
        self.llm_base_object = llm_base(**kwargs)

    def __call__(self, *args, **kwargs):
        task = kwargs["task"]
        assert task is not None
        # method = kwargs.get("method", "GET")
        messages = kwargs.get("messages", None)
        prompt = kwargs.get("prompt", None)
        show_progress = kwargs.get("show_progress", False)
        resp, status = self.llm_base_object(
            messages=messages, system=prompt, show_progress=show_progress
        )
        # output = []
        if not status:
            return resp
        else:
            raise Exception(resp)


class testner(BaseModel):
    sample: Dict[str, List]


class LLM:
    def __init__(self, **kwargs) -> None:
        self._llm = caller(**kwargs)
        self.data = kwargs.get("data", None)
        self.prompt = kwargs.get("prompt", None)
        self.backup_prompt = kwargs.get("prompt", None)
        self.example = kwargs.get("examples", [])
        if not self.example and self.data:
            raise Exception(
                "Please supply a data object or examples as keyword arguments"
            )

        self.examples = kwargs.get("examples", [])
        self.additional_info = kwargs.get("labels", None)
        self.task = kwargs.get("task", None)
        if self.task is not None:
            self.format_control = MAPPING_DICT.get(self.task, None)
            if self.format_control is None:
                raise Exception(
                    f"Task name is not valid - please select one of the following\n "
                    f"{list(MAPPING_DICT.keys())}"
                )

        self._validate_prompt()
        self.format_prompt()
        self.temp_prompt = None

    def _validate_prompt(self):
        prompt_dict = {
            "examples": self.example,
            "labels": self.additional_info,
            "prompt": self.prompt,
        }

        if self.task == "text-classifier":
            try:
                ne = textclassifierprompt(**prompt_dict)
            except:
                raise Exception(
                    f"{self.task} requires the examples in the below format \n"
                    f"Pydantic Schema: Dict[str, List]\n"
                    f"Example: {TASK_EXAMPLE[self.task]}"
                )
            ne._valid()
            self.example = ne._format_example()

        elif self.task == "ner":
            try:
                ne = nerprompt(**prompt_dict)
            except:
                raise Exception(
                    f"{self.task} requires the examples in the below format \n"
                    f"Pydantic Schema: Dict[str, List]\n"
                    f"Example: {TASK_EXAMPLE[self.task]}"
                )
            ne._valid()
            self.example = ne._format_example()
        else:
            return None

    def get_prompt(self):
        return self.prompt

    def add_context(self, context):
        self.temp_prompt = f"{self.prompt}\n\nContext: {context}"

    def process(self, user_input, show_progress=False, task=None):
        results = []
        prompt_token_length = 0

        if isinstance(user_input, str):
            messages = [user_input]
        else:
            messages = user_input

        if self.temp_prompt is not None:
            resp = self._llm(
                messages=messages,
                prompt=self.temp_prompt,
                task=task,
                show_progress=show_progress,
            )
        else:
            resp = self._llm(
                messages=messages,
                prompt=self.prompt,
                task=task,
                show_progress=show_progress,
            )
        return LLM.format_result(resp, self.task)

    @staticmethod
    def format_result(results, task="classification"):
        # Check for the nearest python native object
        response = None
        if len(results) > 0:
            # check the first reponse
            try:
                type_resp = ast.literal_eval(results[0])
                if isinstance(type_resp, dict):
                    response = {}
                    if task == "ner":
                        for idx, i in enumerate(results):
                            response[idx] = {}

                            for key, val in ast.literal_eval(i).items():
                                try:
                                    testner(**{"sample": val})
                                    response[idx] = val
                                except:
                                    response[idx] = {}
                    else:
                        for idx, i in enumerate(results):
                            try:
                                i = ast.literal_eval(i)
                                if len(i):
                                    for key, val in i.items():
                                        if isinstance(val, list):
                                            response[idx] = ",".join(val)
                                        elif isinstance(val, str):
                                            response[idx] = val
                                        elif isinstance(val, dict):
                                            val = list(val.values())[0]
                                            if len(val):
                                                response[idx] = val
                                            else:
                                                response[idx] = ""
                                else:
                                    response[idx] = ""
                            except:
                                response[idx] = ""

                elif isinstance(type_resp, list):
                    response = []
                    for i in results:
                        response += ast.literal_eval(i)

                elif isinstance(type_resp, tuple):
                    response = []
                    for i in results:
                        response += list(ast.literal_eval(i))
            except:
                if isinstance(
                    results[0], str
                ):  # as literal_eval is safe and hence raises an error while we try to evaluate a string
                    response = []
                    for i in results:
                        response.append(i)
                else:
                    warnings.warn(
                        "Unable to interpret the output format, returning the raw response."
                    )
        if response is not None:
            return response
        else:
            return results

    def format_prompt(self):
        if self.example is not None:
            example_formatted = [
                f"### Example {idx} \n\n {i}\n\n" for idx, i in enumerate(self.example)
            ]
        else:
            example_formatted = []

        if len(example_formatted):
            t = "\n".join(
                example_formatted
            )  # have to do it ourside due to limitation of f-string
            prompt = f"{self.prompt}\n\nBelow are the representative examples\n\n{t}"
        else:
            prompt = f"{self.prompt}\n\n {','.join(example_formatted)}"

        if self.additional_info is not None:
            label_temp = self._parse_and_return()
            prompt = f"{prompt} \n\n Following are the classes: \n {label_temp} "
        # attach the format control
        self.prompt = f"{prompt} \n\n {self.format_control['end_seq']}"
        # add the System prompt for the user
        self.prompt = f"{SYSTEM_PROMPT}\n\n{self.prompt}"
        # return prompt

    def _check_abusive(self):
        pass

    def _parse_and_return(self):
        if isinstance(self.additional_info, (list, tuple)):
            return ",".join(self.additional_info)
        elif isinstance(self.additional_info, dict):
            return ",".join(self.additional_info.keys())
        else:
            raise Exception("Could not parse the labels")
