import player
import lib

import json

class Werewolf(player.agent.Agent):
    def __init__(self, config_path: str, name: str) -> None:
        super().__init__(config_path, name)

    def parse_info(self, receive: str) -> None:
        return super().parse_info(receive)

    def get_info(self):
        return super().get_info()

    def initialize(self) -> None:
        return super().initialize()

    def daily_initialize(self) -> None:
        return super().daily_initialize()

    def daily_finish(self) -> None:
        return super().daily_finish()

    def get_name(self) -> str:
        return super().get_name()

    def get_role(self) -> str:
        return super().get_role()

    def talk(self) -> str:
        return super().talk()

    def vote(self) -> str:
        return super().vote()

    def whisper(self) -> None:
        return super().whisper()

    def attack(self):
        attack_target = lib.util.random_select(self.alive)
        print(f"Agent[0{self.index}](me) I attacked Agent[0{attack_target}].")
        data = {"agentIdx": attack_target}

        return json.dumps(data,separators=(",",":"))

    def action(self) -> str:

        if self.request == "ATTACK":
            return self.attack()
        else:
            return super().action()
