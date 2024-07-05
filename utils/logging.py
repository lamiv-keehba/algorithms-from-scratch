from logging import basicConfig, getLogger, INFO #, DEBUG

basicConfig(
    # level=DEBUG,
    level=INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = getLogger()