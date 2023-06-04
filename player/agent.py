import json
from lib import util, log

ROLE_JAPANESE = {"VILLAGER": "村人", "WEREWOLF": "人狼",
                 "SEER": "占い師", "POSSESSED": "狂人"}

logger = log.get_logger(__name__)


class Agent:
    def __init__(self, config_path: str, name: str) -> None:
        self.name = name
        self.received = []
        self.gameContinue = True

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

        self.gameInfo = data["gameInfo"]
        self.gameSetting = data["gameSetting"]
        self.request = data["request"]
        self.talkHistory = data["talkHistory"] or []
        self.whisperHistory = data["whisperHistory"]
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

    def daily_finish(self) -> None:
        pass

    def get_name(self) -> str:
        return self.name

    def get_role(self) -> str:
        return self.role

    def talk(self) -> str:
        return util.random_select(self.comments)

    def vote(self) -> str:
        print("GM: Now, vote for the agent you want to execute.")
        vote_target = util.random_select(self.alive)
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
            self.gameContinue = False

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
