import sys
import logging
from colorlog import ColoredFormatter

logger_fmt = "%(log_color)s%(levelname)-6s%(reset)s| %(bold_blue)s%(asctime)s <%(module)s> %(funcName)s:%(lineno)s %(reset)s-> %(log_color)s%(message)s" # noqa
default_fmt = "%(log_color)s%(levelname)-5s%(reset)s| %(bold_blue)s%(asctime)s %(filename)s:%(funcName)s %(lineno)s%(reset)s-> %(log_color)s%(message)s"  # noqa


def logger(
        name=__file__,
        save_path=None,
        fmt= default_fmt # noqa
) -> logging.Logger:
    formatter = ColoredFormatter(   # debug上控制台去看去
        fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'bold_cyan',
            'INFO': 'bold_green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    file_formatter = ColoredFormatter(      # 日志不输出debug, 推送给千乘
        fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        style='%',
        no_color=True
    )

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    if save_path:
        file_handler = logging.FileHandler(save_path, encoding='utf8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        log.addHandler(file_handler)
    return log


log = logger(logger_fmt)
