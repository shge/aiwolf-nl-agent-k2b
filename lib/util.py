import os
import errno
import configparser
import random
import player
import re
import openai

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def read_text(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def random_select(data: list):
    return random.choice(data)


def is_json_complete(responses: bytes) -> bool:

    try:
        responses = responses.decode("utf-8")
    except:
        return False

    if responses == "":
        return False

    cnt = 0

    for word in responses:
        if word == "{":
            cnt += 1
        elif word == "}":
            cnt -= 1

    return cnt == 0


def init_role(agent: player.agent.Agent, config_path: str, name: str):
    if agent.role == "VILLAGER":
        new_agent = player.villager.Villager(
            config_path=config_path, name=name)
    elif agent.role == "WEREWOLF":
        new_agent = player.werewolf.Werewolf(
            config_path=config_path, name=name)
    elif agent.role == "SEER":
        new_agent = player.seer.Seer(config_path=config_path, name=name)
    elif agent.role == "POSSESSED":
        new_agent = player.possessed.Possessed(
            config_path=config_path, name=name)
    else:
        raise ValueError("role is invalid.")

    agent.hand_over(new_agent=new_agent)

    return new_agent


def check_config(config_path: str) -> configparser.ConfigParser:

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_path)

    return configparser.ConfigParser()


def simplify_agent_name(text: str) -> str:
    # テキスト内の"Agent[03]"→"[3]"に置換する
    return re.sub(r"Agent\[0(\d)\]", r"[\1]", text)


def restore_agent_name(text: str) -> str:
    # テキスト内の"[3]"→"Agent[03]"に置換する
    return re.sub(r"\[(\d)\]", r"Agent[0\1]", text)


def gpt(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    stream: bool = True,
    max_tokens: int = 4096,
    temperature: float = 0.7,  # 0.0 to 2.0
    top_p: float = 1.0,  # 0.0 to 1.0
    frequency_penalty: float = 0.0,  # -2.0 to 2.0
    presence_penalty: float = 0.0,  # -2.0 to 2.0
    **kwargs
) -> str:

    res = openai.ChatCompletion.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        stream=stream,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        **kwargs
    )
    if stream:
        output_text = ""
        for delta in res:
            if delta:
                content = delta["choices"][0]["delta"].get(  # type: ignore
                    "content")
                if content:
                    output_text += content
                    print(content, end="", flush=True)
        print()
        return output_text
    else:
        return res.choices[0].message.content  # type: ignore
