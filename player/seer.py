from lib import util
import player
import lib
import json

ROLE_JAPANESE = {"VILLAGER": "村人", "WEREWOLF": "人狼",
                 "SEER": "占い師", "POSSESSED": "狂人"}

class Seer(player.agent.Agent):
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

    def divine(self) -> str:
        talk_history = ""
        for talk in self.talkHistory:
            talk_history += f"Agent[0{talk['agent']}]: {talk['text']}\n"

        alive_with_self = self.alive.copy()
        alive_with_self.append(self.index)
        alive_with_self.sort()

        if talk_history:
            talk_history = util.gpt(f"""This is talk history of Werewolf game. Summarize what was discussed in bullet points in English.
e.g. [1], [2] are the players' name. Just output as it is.
Do not create new sentences. Just summarize what was discussed.

Talk history
====
{util.simplify_agent_name(talk_history)}""", model="gpt-3.5-turbo")

        vote_target = util.choose_agent(f"""Act as a player in the werewolf game.
# Rules
There are five players in this game, two VILLAGERs (村人), one SEER (占い師), one WEREWOLF (人狼), and one POSSESSED (狂人).
VILLAGER and SEER are on the villager team (村人陣営), and the WEREWOLF and POSSESSED are on the werewolf team (人狼陣営).
SEER can divine the role of one player every day, and usually tells the result to the other players. (黒出し for WEREWOLF, 白出し for others)
If there is only one player claiming SEER, don't just trust yet. Usually two or more players claim SEER.
Players can vote for one player to be executed every day. The player with the most votes will be executed.
WEREWOLF can kill one player every night.
Players can fake their role, but they must not tell their real role.

# Info
Your name is Agent[0{self.index}]. Your role is {self.role} ({ROLE_JAPANESE[self.role]}).
Now, the game is in Day {self.gameInfo['day']}.
Alive players: {', '.join(map(lambda x: f'Agent[0{x}]', alive_with_self))}

Here are the talk history.

# Talk history

{talk_history}

# Divine Result
{self.gameInfo["divineResult"]}

Now, decide which player to divine (who you believe is WEREWOLF).
Don't divine the player who is already divined.
Let's think step by step.""", self.alive)

        data = {"agentIdx": vote_target}

        return json.dumps(data, separators=(",", ":"))


    def action(self) -> str:

        if self.request == "DIVINE":
            return self.divine()
        else:
            return super().action()
