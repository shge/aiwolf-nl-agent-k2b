import lib
import player


def main(config_path: str, name: str):
    logger = lib.log.get_logger(__name__)

    client = lib.client.Client(config_path=config_path)
    logger.debug(f"Connecting to {client.host}:{client.port}...")
    try:
        client.connect()
    except ConnectionRefusedError as e:
        logger.error(f"Connection refused. Check the connection settings in {config_path}.")
        return
    logger.debug("Successfully connected.")

    agent = player.agent.Agent(config_path=config_path, name=name)

    while agent.gameContinue:

        # receivedキューに入っていなかったら入れる
        if len(agent.received) == 0:
            agent.parse_info(receive=client.receive())

        # receivedキューから情報を取り出す
        agent.get_info()
        logger.debug(f"Request: {agent.request}")

        message = agent.action()

        if agent.request == "INITIALIZE":
            agent = lib.util.init_role(
                agent=agent, config_path=config_path, name=name)

        if message != "":
            client.send(message=message)
            logger.debug(f"Sent: {message}")

    client.close()


if __name__ == "__main__":
    config_path = "./res/config.ini"

    inifile = lib.util.check_config(config_path=config_path)
    inifile.read(config_path, "UTF-8")

    main(config_path=config_path, name=inifile.get("agent", "name"))
