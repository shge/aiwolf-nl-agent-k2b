import os
import datetime
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO


def get_logger(module_name: str):

    dark_gray = '\x1b[38;5;240m'
    reset = '\x1b[0m'

    logger = getLogger(module_name)
    logger.setLevel(DEBUG)
    logger.propagate = False

    stream_formatter = Formatter(
        f"{dark_gray}%(asctime)s %(name)s:%(lineno)s %(funcName)s [{reset}%(levelname)s{dark_gray}] {reset}%(message)s")
    stream_handler = StreamHandler()
    stream_handler.setLevel(INFO)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    logs_dir_name = "logs"
    os.makedirs(logs_dir_name, exist_ok=True)
    jst_offset = 9
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=jst_offset))
    )
    file_name = dt_now_jst_aware.strftime("%Y%m%d_%H%M%S") + ".log"
    file_path = os.path.join(logs_dir_name, file_name)
    file_formatter = Formatter(
        "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s] %(message)s")
    file_handler = FileHandler(file_path)
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
