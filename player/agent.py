import json
from lib import util, log
import re

ROLE_JAPANESE = {"VILLAGER": "村人", "WEREWOLF": "人狼",
                 "SEER": "占い師", "POSSESSED": "狂人"}

logger = log.get_logger(__name__)


class Agent:
    def __init__(self, config_path: str, name: str) -> None:
        self.name = name
        self.received = []
        self.gameContinue = True
        self.is_greeting_done = False
        self.today_my_talk_count = 0

        inifile = util.check_config(config_path=config_path)
        inifile.read(config_path, "UTF-8")

        randomTalk = inifile.get("randomTalk", "path")
        _ = util.check_config(randomTalk)

        self.comments = util.read_text(randomTalk)

    def parse_info(self, receive: str) -> None:

        received_list = receive.split("}\n{")

        for received in received_list:
            received = received.rstrip()

            if received[0] != "{":
                received = "{" + received
            if received[-1] != "}":
                received += "}"
            self.received.append(received)

    def get_info(self):
        data = json.loads(self.received.pop(0))

        if data["gameInfo"]:
            self.gameInfo = data["gameInfo"]
        if data["gameSetting"]:
            self.gameSetting = data["gameSetting"]
        self.request = data["request"]
        self.talkHistory = data["talkHistory"] or []
        self.whisperHistory = data["whisperHistory"]
        logger.debug(f"Received: {data}")
        for talk in self.talkHistory:
            logger.info(f"Agent[0{talk['agent']}]: {talk['text']}")

        # if self.gameInfo:
        #     print(f"Day: {self.gameInfo['day']}")
        #     print(f"Divine result: {self.gameInfo['divineResult']}")
        #     print(f"Executed agent: {self.gameInfo['executedAgent']}")
        #     print(f"Latest executed agent: {self.gameInfo['latestExecutedAgent']}")
        #     print(f"Vote list: {self.gameInfo['voteList']}")
        #     print(f"Latest vote list: {self.gameInfo['latestVoteList']}")
        #     print(f"talkList: {self.gameInfo['talkList']}")
        #     print(f"englishTalkList: {self.gameInfo['englishTalkList']}")
        #     print(f"lastDeadAgentList: {self.gameInfo['lastDeadAgentList']}")

    def initialize(self) -> None:
        self.index = self.gameInfo["agent"]
        self.role = self.gameInfo["roleMap"][str(self.index)]
        logger.info(f"Name: Agent[0{self.index}]")
        logger.info(f"Role: {self.role} ({ROLE_JAPANESE[self.role]})")

    def daily_initialize(self) -> None:
        self.alive = []

        for agent_num in self.gameInfo["statusMap"]:
            if self.gameInfo["statusMap"][agent_num] == "ALIVE" and int(agent_num) != self.index:
                self.alive.append(int(agent_num))
        self.alive.sort()

        print()
        print(
            f"================ Day {self.gameInfo['day']} =================")
        if len(self.gameInfo['voteList']) != 0:
            print(
                f"GM: The vote result of Day {self.gameInfo['day'] - 1} is as follows:")
            for vote in self.gameInfo['voteList']:
                print(
                    f"GM: Agent[0{vote['agent']}] voted for Agent[0{vote['target']}].")
        if self.gameInfo["executedAgent"] != -1:
            print(
                f"GM: Agent[0{self.gameInfo['executedAgent']}] was executed as a result of the vote.")
        if self.gameInfo["lastDeadAgentList"] != []:
            print(
                f"GM: Agent[0{self.gameInfo['lastDeadAgentList'][0]}] was attacked by a werewolf.")
        if self.gameInfo['divineResult']:
            print(
                f"GM: Here is the result of the divine: {self.gameInfo['divineResult']}")
        print(
            f"GM: Alive agents are as follows: {', '.join(map(lambda x: f'Agent[0{x}]', self.alive))}")
        if self.gameInfo['day'] >= 1:
            print("GM: Now, start the discussion and choose who to vote for.")

        self.today_my_talk_count = 0

    def daily_finish(self) -> None:
        pass

    def get_name(self) -> str:
        return self.name

    def get_role(self) -> str:
        return self.role

    # def count_over(self) -> int:
    #     count = 0
    #     for talk in self.talkHistory:
    #         if talk['text'] == "Over":
    #             count += 1
    #     print("count_over: ", count)
    #     return count

    def talk(self) -> str:
        if self.gameInfo["day"] == 0:
            if self.is_greeting_done:
                return "Over"
            else:
                return self.talk_day0()
        # return util.random_select(self.comments)
        print(self.today_my_talk_count)
        if self.today_my_talk_count > 5:
            return "Over"
        self.today_my_talk_count += 1
        return self.make_answer()

    def talk_day0(self) -> str:
        self.is_greeting_done = True
        return util.random_select(util.read_text("./res/greeting.csv")).split(",")[1]

    def vote(self) -> str:
        print("GM: Now, vote for the agent you want to execute.")
        # vote_target = util.random_select(self.alive)

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

Now, decide which player to vote for (who you believe is WEREWOLF).
Let's think step by step.""", self.alive)

        print(f"Agent[0{self.index}](me) voted for Agent[0{vote_target}].")
        data = {"agentIdx": vote_target}

        return json.dumps(data, separators=(",", ":"))

    def whisper(self) -> None:
        pass

    def finish(self) -> None:
        logger.info("================ Game Finished ================")
        logger.info(
            f"GM: The vote result of Day {self.gameInfo['day'] - 1} is as follows:")
        for vote in self.gameInfo['voteList']:
            logger.info(
                f"GM: Agent[0{vote['agent']}] voted for Agent[0{vote['target']}].")
        if self.gameInfo["executedAgent"] != -1:
            logger.info(
                f"GM: Agent[0{self.gameInfo['executedAgent']}] was executed as a result of the vote.")
        if self.gameInfo["lastDeadAgentList"] != []:
            logger.info(
                f"GM: Agent[0{self.gameInfo['lastDeadAgentList'][0]}] was attacked by a werewolf.")
        logger.info("")
        logger.info("GM: The game is over.")
        logger.info("")
        logger.info("GM: The result is as follows:")
        for i in range(1, 6):
            logger.info(
                f"GM: Agent[0{i}] was {self.gameInfo['roleMap'][str(i)]} ({self.gameInfo['statusMap'][str(i)]}).")
        werewolf_agent_num = [agent_num for agent_num in self.gameInfo['roleMap']
                              if self.gameInfo['roleMap'][agent_num] == "WEREWOLF"][0]
        winner_team = "VILLAGER" if self.gameInfo['statusMap'][werewolf_agent_num] == "DEAD" else "WEREWOLF"
        logger.info("")
        logger.info(f"GM: The winner team is {winner_team}.")
        if (self.role == "WEREWOLF" or self.role == "POSSESSED") and winner_team == "WEREWOLF":
            logger.info("GM: Your team won! Congratulations! 🎉")
        else:
            logger.info("GM: Your team lost.")

    def action(self) -> str:

        if self.request == "INITIALIZE":
            self.initialize()
        elif self.request == "NAME":
            return self.get_name()
        elif self.request == "ROLE":
            return self.get_role()
        elif self.request == "DAILY_INITIALIZE":
            self.daily_initialize()
        elif self.request == "DAILY_FINISH":
            self.daily_finish()
        elif self.request == "TALK":
            return self.talk()
        elif self.request == "VOTE":
            return self.vote()
        elif self.request == "WHISPER":
            self.whisper()
        elif self.request == "FINISH":
            self.finish()
            # self.gameContinue = False

        return ""

    def hand_over(self, new_agent) -> None:
        # __init__
        new_agent.name = self.name
        new_agent.received = self.received
        new_agent.gameContinue = self.gameContinue
        new_agent.comments = self.comments

        # get_info
        new_agent.gameInfo = self.gameInfo
        new_agent.gameSetting = self.gameSetting
        new_agent.request = self.request
        new_agent.talkHistory = self.talkHistory
        new_agent.whisperHistory = self.whisperHistory

        # initialize
        new_agent.index = self.index
        new_agent.role = self.role

    def make_answer(self) -> str:
        alive_with_self = self.alive.copy()
        alive_with_self.append(self.index)
        alive_with_self.sort()
        talk_history = ""
        for talk in self.talkHistory:
            talk_history += f"Agent[0{talk['agent']}]: {talk['text']}\n"

        if talk_history:
            talk_history = util.gpt(f"""This is talk history of Werewolf game. Summarize what was discussed in bullet points in English.
e.g. [1], [2] are the players' name. Just output as it is.
Do not create new sentences. Just summarize what was discussed.

Talk history
====
{util.simplify_agent_name(talk_history)}""", model="gpt-3.5-turbo")

        prompt = f"""Act as a player in the werewolf game in Japanese. 口調はおばさん口調でお願いします。
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

Make a statement to persuade other players logically based on others' statements.
Speak casually but confidently in Japanese. Answer must be concise and to the point.
To mention other players, say [1], [2], [3], [4] or [5].

# Tips on your role: {self.role} ({ROLE_JAPANESE[self.role]})
Don't tell other players about tips below.
{self.make_tips()}
{"Since this is Day 0, SEER can't select which player to divine. No need to ask why." if self.gameInfo['day'] == 0 else ""}
{"Since this is Day 2, keep in mind that SEER might be attacked by WEREWOLF and no longer exist in the village." if self.gameInfo['day'] == 2 and self.role != "SEER" else ""}

Let's think step by step.
State who you think is the WEREWOLF. Form everyone's opinions.

Now, make a output in the following format:
Agent[0{self.index}]: [Your statement in Japanese (No English translation)]
"""
        simplified_prompt = util.simplify_agent_name(prompt)
        print("===========================================")
        # print(simplified_prompt)
        print("===========================================")
        answer = util.gpt(simplified_prompt, max_tokens=300, model="gpt-4")
        # answer = util.random_select(self.comments)
        answer = util.restore_agent_name(answer)
        answer = re.sub(r"^Agent\[0(\d)\]: ", "", answer)
        return answer

    def make_tips(self) -> str:
        if self.role == "VILLAGER":
            return """You have no special abilities.
You have to find WEREWOLF and execute him.
Provoke the WEREWOLF or encourage the villagers, especially when there is little information about the WEREWOLF or suspicious players.
Think logically and find out who is lying."""

        elif self.role == "SEER":
            divineResult = self.gameInfo["divineResult"]
            print(divineResult)
            if divineResult:
                text = f"""You can divine one player per night.
On Day {divineResult["day"]}, you divined Agent[0{divineResult["target"]}] and found out he was {divineResult["result"]}"""
                if divineResult["result"] == "WEREWOLF":
                    text += " (黒). \nYou should tell results and persuade players to execute him."
                else:
                    text += " (白). \nYou should tell results and persuade players not to execute him."
                return text
            else:
                return "You can divine one player per night."

        elif self.role == "WEREWOLF":
            return """You must not let other players know you are WEREWOLF.
You have to deceive other players and survive.
If two or more SEER don't appear after some conversations, you had better pretend to be SEER and tell fake results."""

        elif self.role == "POSSESSED":
            return """If there are zero or one player claiming SEER, you had better pretend to be SEER and tell fake results.
Example of fake results: I divined ** and found out he was HUMAN(白)/WEREWOLF(黒).
If there are two or more players claiming SEER, you can pretend to be VILLAGER.
Never reveal you are pretending. Just act as the role."""

        else:
            logger.error(f"Invalid role: {self.role}")
            return ""
