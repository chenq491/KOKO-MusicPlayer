import logging

def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # 添加控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(filename)s %(lineno)d - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)
    return log

logger = get_logger("MusicPlayer")